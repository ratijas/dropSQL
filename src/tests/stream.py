from io import StringIO
from unittest import TestCase

from dropSQL.parser.streams import *


class StreamTestCase(TestCase):
    def test(self):
        s = '12'
        cs = Characters(StringIO(s))

        ch = cs.peek().ok()
        self.assertEqual(ch, '1')

        ch = cs.peek().ok()
        self.assertEqual(ch, '1')

        ch = cs.next().ok()
        self.assertEqual(ch, '1')

        ch = cs.next().ok()
        self.assertEqual(ch, '2')

        r = cs.next()
        self.assertFalse(r)
        self.assertTrue(r.err())

        r = cs.next()
        self.assertFalse(r)

        cs.back()
        r = cs.next()
        self.assertTrue(r)
        self.assertEqual(r.ok(), '2')

        cs.back(2)
        r = cs.next()
        self.assertTrue(r)
        self.assertEqual(r.ok(), '1')
