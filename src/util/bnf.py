"""
check how many times each token name appears in bnf grammar.

if some token appears only once, maybe it is because the token is defined without use,
or worse, is used without definition.
"""

from collections import defaultdict
from pprint import pprint
import re

from dropSQL import parser

WORD = re.compile(r'"?/?(\w+)"?')
ATOM = re.compile(r'"/?(.+?)"')


def words(s: str):
    d = defaultdict(lambda: 0)
    for word in re.findall(WORD, s):
        d[word] += 1

    return dict(d)


def main():
    doc = parser.__doc__

    ws = words(doc)

    singles = {k: v for k, v in ws.items() if v == 1}
    print("singles")
    pprint(singles)
    print()

    atoms = sorted(set(re.findall(ATOM, doc)))
    print("atoms")
    pprint(atoms)
    print()

    rules = sorted(set(ws) - set(atoms))
    print("rules", len(rules))
    pprint(rules)
    print()


if __name__ == '__main__':
    main()
