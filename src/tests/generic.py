from unittest import TestCase

from dropSQL.parser.tokens import Error
from dropSQL.generic import *


class GenericTestCase(TestCase):
    def test_result(self):
        res = Ok(42)
        self.assertTrue(res.is_ok())
        self.assertEqual(res.ok(), 42)

        res = Err(Error(['token'], 'EOF'))
        self.assertTrue(res.is_err())
        self.assertFalse(res.is_ok())
        self.assertIsInstance(res.err(), Error)

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
