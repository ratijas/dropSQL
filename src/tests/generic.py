from unittest import TestCase

from dropSQL.parser.expected import *
from dropSQL.parser.tokens import *
from dropSQL.generic import *


class GenericTestCase(TestCase):
    def test_result(self):
        res = Ok(42)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.ok(), 42)

        res = Err(EOF(['token']))
        self.assertTrue(res.is_err())
        self.assertFalse(res.is_ok())
        self.assertTrue(res.err().eof())

    def test_result_fn(self):
        res: Result[int, None] = Ok(42)
        self.assertTrue(res.is_ok())
        res: Result[int, None] = res.map(lambda x: x + 2)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.ok(), 44)

        res: Result[str, int] = res.and_then(lambda x: Ok('') if None else Err(int(x / 4)))
        self.assertFalse(res.is_ok())
        self.assertEqual(res.err(), 11)

        res: Result[str, float] = res.map_err(float)
        self.assertTrue(res.is_err())
        self.assertIsInstance(res.err(), float)

        ok: str = res.ok_or('abc')
        self.assertEqual(ok, 'abc')

    def test_cast(self):
        i = 5
        res = cast(float)(i)
        self.assertTrue(res.is_err())
        self.assertFalse(res)

        s = TokenStream(Stream('/drop'))
        tok = s.gettok().ok()  # type: Token
        self.assertTrue(cast(Reserved)(tok))
        self.assertTrue(cast(Drop)(tok))
        self.assertFalse(cast(Operator)(tok))

    def test_caster(self):
        cs = cast(int)
        ok = cs(42)
        err = cs(0.3)

        self.assertTrue(ok)
        self.assertFalse(err)

        err = cast(LParen)(Create())
        self.assertFalse(err)
