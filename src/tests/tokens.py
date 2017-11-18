from unittest import TestCase

from dropSQL.parser.expected import Expected
from dropSQL.parser.tokens import *


class ParserTestCase(TestCase):
    def test_identifier(self):
        ident = Identifier('drop', slash=True)
        self.assertEqual('/drop', str(ident))

    def test_eof(self):
        s = Stream('')
        tok = next_token(s)
        self.assertTrue(tok.is_err())
        self.assertIsInstance(tok.err(), Expected)
        self.assertEqual(tok.err().got, 'EOF')

    def test_punctuation(self):
        s = Stream('( , )')
        tok = next_token(s).ok()
        self.assertIsInstance(tok, LParen)
        tok = next_token(s).ok()
        self.assertIsInstance(tok, Comma)
        tok = next_token(s).ok()
        self.assertIsInstance(tok, RParen)
        tok = next_token(s)
        self.assertTrue(tok.is_err())

    def test_more_identifiers(self):
        s = Stream('/create table if not exists /students /drop')
        n = lambda: next_token(s).ok()

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

    def test_literals(self):
        s = Stream('42 15.37 \'UFO\'')

        tok = next_token(s).ok()
        self.assertIsInstance(tok, Integer)
        self.assertEqual(42, tok.value)

        tok = next_token(s).ok()
        self.assertIsInstance(tok, Float)
        self.assertAlmostEqual(15.37, tok.value, 2)

        tok = next_token(s).ok()
        self.assertIsInstance(tok, String)
        self.assertEqual('UFO', tok.value)

        s = Stream(' \'not the...')
        tok = next_token(s)
        self.assertTrue(tok.is_err())

        s = Stream(" 'abc\\' def' ")
        tok = next_token(s).ok()
        self.assertEqual(tok, String("abc' def"))

    def test_comment(self):
        s = Stream('42, -- this is the answer\n'
                   '37  -- while this one is definitely not.\n')
        n = lambda: next_token(s).ok()
        tok = (n(), n(), n(), next_token(s))

        self.assertEqual(tok[0], Integer(42))
        self.assertIsInstance(tok[1], Comma)
        self.assertEqual(tok[2], Integer(37))
        self.assertTrue(tok[3].is_err())

    def test_operators(self):
        s = Stream(
            '  *    >=   >    /=   /    /5        /and')
        n = lambda: next_token(s).ok()

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
        s = Stream('?1, ?32 ? 4')
        n = lambda: next_token(s).ok()
        tok = (n(), n(), n(), next_token(s))

        self.assertEqual(tok[0], Placeholder(1))
        self.assertIsInstance(tok[1], Comma)
        self.assertEqual(tok[2], Placeholder(32))
        self.assertTrue(tok[3].is_err())

    def test_all_keywords(self):
        # @formatter:off
        self.assertIsInstance(next_token(Stream('and')).ok(),        Operator)
        self.assertIsInstance(next_token(Stream('as')).ok(),         As)
        self.assertIsInstance(next_token(Stream('create')).ok(),     Create)
        self.assertIsInstance(next_token(Stream('delete')).ok(),     Delete)
        self.assertIsInstance(next_token(Stream('drop')).ok(),       Drop)
        self.assertIsInstance(next_token(Stream('exists')).ok(),     Exists)
        self.assertIsInstance(next_token(Stream('float')).ok(),      Identifier)
        self.assertIsInstance(next_token(Stream('from')).ok(),       From)
        self.assertIsInstance(next_token(Stream('if')).ok(),         If)
        self.assertIsInstance(next_token(Stream('insert')).ok(),     Insert)
        self.assertIsInstance(next_token(Stream('integer')).ok(),    Identifier)
        self.assertIsInstance(next_token(Stream('into')).ok(),       Into)
        self.assertIsInstance(next_token(Stream('join')).ok(),       Join)
        self.assertIsInstance(next_token(Stream('key')).ok(),        Key)
        self.assertIsInstance(next_token(Stream('not')).ok(),        Not)
        self.assertIsInstance(next_token(Stream('on')).ok(),         On)
        self.assertIsInstance(next_token(Stream('or')).ok(),         Operator)
        self.assertIsInstance(next_token(Stream('primary')).ok(),    Primary)
        self.assertIsInstance(next_token(Stream('select')).ok(),     Select)
        self.assertIsInstance(next_token(Stream('set')).ok(),        Set)
        self.assertIsInstance(next_token(Stream('table')).ok(),      Table)
        self.assertIsInstance(next_token(Stream('update')).ok(),     Update)
        self.assertIsInstance(next_token(Stream('values')).ok(),     Values)
        self.assertIsInstance(next_token(Stream('varchar')).ok(),    Identifier)
        self.assertIsInstance(next_token(Stream('where')).ok(),      Where)
        # @formatter:on
