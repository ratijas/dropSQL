from unittest import TestCase

from dropSQL.ast import *
from dropSQL.parser.streams import *
from dropSQL.parser.tokens.operator import Operator


class ExpressionTestCase(TestCase):
    def test_literal(self) -> None:
        sql = '42'
        expr = Expression.from_sql(Tokens.from_str(sql))
        self.assertTrue(expr)
        self.assertIsInstance(expr.ok(), ExpressionLiteralInt)

        sql = '13.37'
        expr = Expression.from_sql(Tokens.from_str(sql))
        self.assertTrue(expr)
        self.assertIsInstance(expr.ok(), ExpressionLiteralFloat)

        sql = "'hello, world'"
        expr = Expression.from_sql(Tokens.from_str(sql))
        self.assertTrue(expr)
        self.assertIsInstance(expr.ok(), ExpressionLiteralVarChar)

    def test_ref(self) -> None:
        sql = 'ref'
        expr = Expression.from_sql(Tokens.from_str(sql))
        self.assertTrue(expr)
        e = expr.ok()
        self.assertIsInstance(e, ExpressionReference)
        self.assertIsNone(e.table)
        self.assertEqual(e.column, Identifier('ref'))

        sql = 'tab/ref'
        expr = Expression.from_sql(Tokens.from_str(sql))
        self.assertTrue(expr)
        e = expr.ok()
        self.assertIsInstance(e, ExpressionReference)
        self.assertIsNotNone(e.table)
        self.assertEqual(e.table, Identifier('tab'))
        self.assertEqual(e.column, Identifier('ref'))

    def test_placeholder(self) -> None:
        sql = '?42'
        expr = Expression.from_sql(Tokens.from_str(sql))
        self.assertTrue(expr)
        e = expr.ok()
        self.assertIsInstance(e, ExpressionPlaceholder)
        self.assertEqual(e.index, 42)

    def test_paren(self) -> None:
        sql = '(O)'
        expr = Expression.from_sql(Tokens.from_str(sql))
        self.assertTrue(expr)
        e = expr.ok()
        self.assertIsInstance(e, ExpressionParen)
        inner = e.inner
        self.assertIsInstance(inner, ExpressionReference)

    def test_binary(self) -> None:
        sql = '2 + 3'
        expr = Expression.from_sql(Tokens.from_str(sql))
        self.assertTrue(expr)
        e = expr.ok()
        self.assertIsInstance(e, ExpressionBinary)
        self.assertEqual(e.operator.operator, Operator.ADD)
        self.assertEqual(e.lhs, ExpressionLiteralInt(2))

        sql = '(2 + 3) = 5'
        expr = Expression.from_sql(Tokens.from_str(sql))
        self.assertTrue(expr)
        e = expr.ok()
        self.assertIsInstance(e, ExpressionBinary)
        self.assertEqual(e.operator.operator, Operator.EQ)
        self.assertIsInstance(e.lhs, ExpressionParen)
