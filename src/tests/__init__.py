from unittest import TestCase
from dropSQL import parser


class ParserTestCase(TestCase):
    def test_say(self):
        self.assertEqual("hi", parser.say("hi"))
