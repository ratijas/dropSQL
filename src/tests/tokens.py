from io import StringIO
from unittest import TestCase

from dropSQL.parser.streams import *
from dropSQL.parser.tokens import *


class TokensTestCase(TestCase):
    def test_identifier(self):
        ident = Identifier('drop', slash=True)
        self.assertEqual('/drop', str(ident))

    def test_eof(self):
        s = Characters(StringIO(''))
        tok = s.next()
        self.assertTrue(tok.is_err())
        self.assertTrue(tok.err())

    def test_punctuation(self):
        s = Tokens(Characters(StringIO('( , )')))
        tok = s.next().ok()
        self.assertIsInstance(tok, LParen)
        tok = s.next().ok()
        self.assertIsInstance(tok, Comma)
        tok = s.next().ok()
        self.assertIsInstance(tok, RParen)
        res = s.next()
        self.assertFalse(res)

    def test_more_identifiers(self):
        s = Tokens(Characters(StringIO('/create table if not exists /students /drop')))
        n = lambda: s.next().ok()

        tok = (n(), n(), n(), n(), n(), n(), n())
        self.assertIsInstance(tok[0], Create)
        self.assertIsInstance(tok[1], Table)
        self.assertIsInstance(tok[2], If)
        self.assertIsInstance(tok[3], Not)
        self.assertIsInstance(tok[4], Exists)
        self.assertIsInstance(tok[5], Identifier)
        self.assertIsInstance(tok[6], Drop)

        ident: Identifier = tok[5]
        self.assertEqual(ident.identifier, 'students')
        self.assertTrue(ident.slash)

        s = Tokens(Characters(StringIO('/file_id')))
        tok = s.next().ok()
        self.assertEqual(tok, Identifier('file_id'))
        self.assertFalse(s.next())

    def test_next_token_consistent_error(self):
        # FIXME
        s = Tokens(Characters(StringIO('file[id]')))
        res = s.next()
        self.assertTrue(res)
        print('A' * 100)
        res = s.next()
        print('res:', res)
        self.assertFalse(res)
        self.assertEqual(res.err().got, '[')
        res = s.next()
        self.assertFalse(res)

    def test_literals(self):
        s = Tokens(Characters(StringIO('42 15.37 \'UFO\'')))

        tok = s.next().ok()
        self.assertIsInstance(tok, Integer)
        self.assertEqual(42, tok.value)

        tok = s.next().ok()
        self.assertIsInstance(tok, Float)
        self.assertAlmostEqual(15.37, tok.value, 2)

        tok = s.next().ok()
        self.assertIsInstance(tok, VarChar)
        self.assertEqual('UFO', tok.value)

        s = Tokens(Characters(StringIO(' \'not the...')))
        tok = s.next()
        self.assertTrue(tok.is_err())

        s = Tokens(Characters(StringIO(" 'abc\\' def' ")))
        tok = s.next().ok()
        self.assertEqual(tok, VarChar("abc' def"))

    def test_comment(self):
        s = Tokens(Characters(StringIO('42, -- this is the answer\n'
                                       '37  -- while this one is definitely not.\n')))
        n = lambda: s.next().ok()
        tok = (n(), n(), n(), s.next())

        self.assertEqual(tok[0], Integer(42))
        self.assertIsInstance(tok[1], Comma)
        self.assertEqual(tok[2], Integer(37))
        self.assertTrue(tok[3].is_err())

    def test_operators(self):
        s = Tokens(Characters(StringIO(
            '  *    >=   >    /=   /    /5        /and')))
        n = lambda: s.next().ok()

        tok = (n(), n(), n(), n(), n(), n(), n(), n())
        self.assertEqual(tok[0], Operator('*'))
        self.assertEqual(tok[1], Operator('>='))
        self.assertEqual(tok[2], Operator('>'))
        self.assertEqual(tok[3], Operator('/='))
        self.assertEqual(tok[4], Operator('/'))
        self.assertEqual(tok[5], Operator('/'))
        self.assertEqual(tok[6], Integer(5))
        self.assertEqual(tok[7], Operator('/and'))

    def test_placeholder(self):
        s = Tokens(Characters(StringIO('?1, ?32 ? 4')))
        n = lambda: s.next().ok()
        tok = (n(), n(), n(), s.next())

        self.assertEqual(tok[0], Placeholder(1))
        self.assertIsInstance(tok[1], Comma)
        self.assertEqual(tok[2], Placeholder(32))
        self.assertTrue(tok[3].is_err())

    def test_all_keywords(self):
        def next_token(s: str) -> Token:
            return Tokens(Characters(StringIO(s))).next().ok()

        # @formatter:off
        self.assertIsInstance(next_token('and'),        Operator)
        self.assertIsInstance(next_token('as'),         As)
        self.assertIsInstance(next_token('create'),     Create)
        self.assertIsInstance(next_token('delete'),     Delete)
        self.assertIsInstance(next_token('drop'),       Drop)
        self.assertIsInstance(next_token('exists'),     Exists)
        self.assertIsInstance(next_token('float'),      Identifier)
        self.assertIsInstance(next_token('from'),       From)
        self.assertIsInstance(next_token('if'),         If)
        self.assertIsInstance(next_token('insert'),     Insert)
        self.assertIsInstance(next_token('integer'),    Identifier)
        self.assertIsInstance(next_token('into'),       Into)
        self.assertIsInstance(next_token('join'),       Join)
        self.assertIsInstance(next_token('key'),        Key)
        self.assertIsInstance(next_token('not'),        Not)
        self.assertIsInstance(next_token('on'),         On)
        self.assertIsInstance(next_token('or'),         Operator)
        self.assertIsInstance(next_token('primary'),    Primary)
        self.assertIsInstance(next_token('select'),     Select)
        self.assertIsInstance(next_token('set'),        SetKw)
        self.assertIsInstance(next_token('table'),      Table)
        self.assertIsInstance(next_token('update'),     Update)
        self.assertIsInstance(next_token('values'),     Values)
        self.assertIsInstance(next_token('varchar'),    Identifier)
        self.assertIsInstance(next_token('where'),      Where)
        # @formatter:on
