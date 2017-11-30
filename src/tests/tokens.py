from unittest import TestCase

from dropSQL.parser.streams import *
from dropSQL.parser.tokens import *


class TokensTestCase(TestCase):
    def test_identifier(self):
        ident = Identifier('drop', slash=True)
        self.assertEqual('/drop', str(ident))

    def test_eof(self):
        s = Characters.from_str('')
        tok = s.next()
        self.assertTrue(tok.is_err())
        self.assertTrue(tok.err())

    def test_punctuation(self):
        s = Tokens(Characters.from_str('( , )'))
        tok = s.next().ok()
        self.assertIsInstance(tok, LParen)
        tok = s.next().ok()
        self.assertIsInstance(tok, Comma)
        tok = s.next().ok()
        self.assertIsInstance(tok, RParen)
        res = s.next()
        self.assertFalse(res)

    def test_more_identifiers(self):
        s = Tokens(Characters.from_str('/create table if not exists /students /drop'))
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

        s = Tokens(Characters.from_str('/file_id'))
        tok = s.next().ok()
        self.assertEqual(tok, Identifier('file_id'))
        self.assertFalse(s.next())

    def test_next_token_consistent_error(self):
        s = Tokens(Characters.from_str('file[id]'))
        res = s.next()
        self.assertTrue(res)
        res = s.next()
        self.assertFalse(res)
        self.assertEqual(res.err().got, '[')
        res = s.next()
        self.assertFalse(res)

    def test_literals(self):
        s = Tokens.from_str('42 15.37 \'UFO\'')

        tok = s.next().ok()
        self.assertIsInstance(tok, Integer)
        self.assertEqual(42, tok.value)

        tok = s.next().ok()
        self.assertIsInstance(tok, Float)
        self.assertAlmostEqual(15.37, tok.value, 2)

        tok = s.next().ok()
        self.assertIsInstance(tok, VarChar)
        self.assertEqual('UFO', tok.value)

        s = Tokens.from_str(' \'not the...')
        tok = s.next()
        self.assertTrue(tok.is_err())

        s = Tokens.from_str(" 'abc\\' def' ")
        tok = s.next().ok()
        self.assertEqual(tok, VarChar("abc' def"))

    def test_comment(self):
        s = Tokens.from_str('42, -- this is the answer\n'
                            '37  -- while this one is definitely not.\n')
        n = lambda: s.next().ok()
        tok = (n(), n(), n(), s.next())

        self.assertEqual(tok[0], Integer(42))
        self.assertIsInstance(tok[1], Comma)
        self.assertEqual(tok[2], Integer(37))
        self.assertTrue(tok[3].is_err())

    def test_operators(self):
        s = Tokens(Characters.from_str((
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
        s = Tokens.from_str('?1, ?32 ? 4')
        n = lambda: s.next().ok()
        tok = (n(), n(), n(), s.next())

        self.assertEqual(tok[0], Placeholder(1))
        self.assertIsInstance(tok[1], Comma)
        self.assertEqual(tok[2], Placeholder(32))
        self.assertTrue(tok[3].is_err())

    def test_all_keywords(self):
        def tok(s: str) -> Token:
            return Tokens.from_str(s).next().ok()

        # @formatter:off
        self.assertIsInstance(tok('and'),        Operator)
        self.assertIsInstance(tok('as'),         As)
        self.assertIsInstance(tok('create'),     Create)
        self.assertIsInstance(tok('delete'),     Delete)
        self.assertIsInstance(tok('drop'),       Drop)
        self.assertIsInstance(tok('exists'),     Exists)
        self.assertIsInstance(tok('float'),      Identifier)
        self.assertIsInstance(tok('from'),       From)
        self.assertIsInstance(tok('if'),         If)
        self.assertIsInstance(tok('insert'),     Insert)
        self.assertIsInstance(tok('integer'),    Identifier)
        self.assertIsInstance(tok('into'),       Into)
        self.assertIsInstance(tok('join'),       Join)
        self.assertIsInstance(tok('key'),        Key)
        self.assertIsInstance(tok('not'),        Not)
        self.assertIsInstance(tok('on'),         On)
        self.assertIsInstance(tok('or'),         Operator)
        self.assertIsInstance(tok('primary'),    Primary)
        self.assertIsInstance(tok('select'),     Select)
        self.assertIsInstance(tok('set'),        SetKw)
        self.assertIsInstance(tok('table'),      Table)
        self.assertIsInstance(tok('update'),     Update)
        self.assertIsInstance(tok('values'),     Values)
        self.assertIsInstance(tok('varchar'),    Identifier)
        self.assertIsInstance(tok('where'),      Where)
        # @formatter:on
