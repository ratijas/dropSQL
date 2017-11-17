#!/usr/bin/env python

from setuptools import setup
from os.path import join, dirname
import sys

sys.path.append(join(dirname(__file__), 'src'))

from dropSQL import __version__ as version

setup(
    name='dropSQL',
    version=version,
    description='Simple database engine and binary format. Yet another university sucksignment.',
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    author='ratijas & ecat3',
    author_email='gmail@ratijas.tk',
    url='https://github.com/ratijas/dropSQL',
    packages=['dropSQL'],
    package_dir={'dropSQL': 'src/dropSQL'},
    entry_points={
        'console_scripts':
            ['dropSQL = dropSQL.repl:launch']
    },
    test_suite='src.tests',
)
