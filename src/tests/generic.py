from unittest import TestCase

from dropSQL.generic import *
from dropSQL.parser.tokens import *


class GenericTestCase(TestCase):
    def test_result(self):
        res = Ok(42)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.ok(), 42)

        res = Err(Incomplete())
        self.assertTrue(res.is_err())
        self.assertFalse(res.is_ok())
        self.assertTrue(res.err())

    def test_result_fn(self):
        res = Ok(42)  # type: Result[int, None]
        self.assertTrue(res.is_ok())
        res = res.map(lambda x: x + 2)  # type: Result[int, None]
        self.assertTrue(res.is_ok())
        self.assertEqual(res.ok(), 44)

        res = res.and_then(lambda x: Ok('') if None else Err(int(x / 4)))  # type: Result[str, int]
        self.assertFalse(res.is_ok())
        self.assertEqual(res.err(), 11)

        ok: str = res.ok_or('abc')
        self.assertEqual(ok, 'abc')

    def test_cast(self):
        i = 5
        res = Cast(float)(i)
        self.assertTrue(res.is_err())
        self.assertFalse(res)

        tok: Token = Drop()
        self.assertTrue(Cast(Keyword)(tok))
        self.assertTrue(Cast(Drop)(tok))
        self.assertFalse(Cast(Operator)(tok))

    def test_caster(self):
        cs = Cast(int)
        ok = cs(42)
        err = cs(0.3)

        self.assertTrue(ok)
        self.assertFalse(err)

        err = Cast(LParen)(Create())
        self.assertFalse(err)
