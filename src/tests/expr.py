from unittest import TestCase

from dropSQL.ast import *
from dropSQL.engine.column import Column
from dropSQL.engine.context import Context
from dropSQL.engine.row_set import *
from dropSQL.parser.tokens import Operator


class ExprTestCase(TestCase):
    def test_literal(self) -> None:
        ctx = Context.empty()

        self.assertEqual(42, ExpressionLiteralInt(42).eval_with(ctx).ok())
        self.assertEqual(1.0, ExpressionLiteralFloat(1.0).eval_with(ctx).ok())
        self.assertEqual('abc', ExpressionLiteralVarChar('abc').eval_with(ctx).ok())

    def test_paren(self) -> None:
        ctx = Context.empty()

        self.assertEqual(42, ExpressionParen(ExpressionLiteralInt(42)).eval_with(ctx).ok())

    def test_binary(self) -> None:
        ctx = Context.empty()

        self.assertEqual(42, ExpressionBinary(
            Operator(Operator.ADD),
            ExpressionLiteralInt(40),
            ExpressionLiteralInt(2)
        ).eval_with(ctx).ok())

        # types
        self.assertIsInstance(
            ExpressionBinary(
                Operator(Operator.MUL),
                ExpressionLiteralFloat(1.0),
                ExpressionLiteralInt(42)
            ).eval_with(ctx).ok(),
            float)

        # float times str
        self.assertFalse(ExpressionBinary(
            Operator(Operator.MUL),
            ExpressionLiteralFloat(4.0),
            ExpressionLiteralVarChar('abc'),
        ).eval_with(ctx))

    def test_placeholder(self) -> None:
        ctx = Context.empty()
        ctx.args = (42, 1.5, 'morty')

        self.assertEqual(42, ExpressionPlaceholder(1).eval_with(ctx).ok())
        self.assertFalse(ExpressionPlaceholder(4).eval_with(ctx))

    def test_reference(self) -> None:
        rs = MockRowSet(
            [Column(Identifier('person'), Identifier('name'), VarCharTy(64)),
             Column(Identifier('person'), Identifier('age'), IntegerTy()),
             Column(Identifier('meta'), Identifier('height'), FloatTy())],
            [['morty', 11, 144.],
             ['jimmy', 10, 157.],
             ['jerry', 30, 180.5]])

        it = rs.iter()

        ctx = Context(next(it), ())
        ref = ExpressionReference(Identifier('person'), Identifier('name')).eval_with(ctx).ok()
        self.assertEqual('morty', ref)

        ctx = Context(next(it), ())
        ref = ExpressionReference(None, Identifier('height')).eval_with(ctx).ok()
        self.assertEqual(157., ref)
