from unittest import TestCase

from dropSQL.parser.streams.statements import Statements


class StatementsTestCase(TestCase):
    def test_drop(self) -> None:
        s = Statements.from_str('/drop table person /drop\n'
                                '/drop table if exists files /drop\n'
                                '/delete from /friends /where 1 /= 2 /drop\n')
        stmts = s.collect()
        self.assertTrue(stmts)
        self.assertEqual(len(stmts.ok()), 3)
