from unittest import TestCase

from dropSQL.ast import *
from dropSQL.parser.streams import *


class UpdateSetTestCase(TestCase):
    def test(self) -> None:
        sql = "/update friends /set age = age + 1, /hair = 'curly' /where name = 'morty' /drop"
        res = UpdateSet.from_sql(Tokens.from_str(sql))
        self.assertTrue(res)
        us = res.ok()
        self.assertIsNotNone(us.where)
        self.assertEqual(len(us.assignments), 2)
