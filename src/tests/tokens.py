from unittest import TestCase

from dropSQL import parser
from dropSQL.parser.tokens import *


class ParserTestCase(TestCase):
    def test_say(self):
        self.assertEqual("hi", parser.say("hi"))

    def test_identifier(self):
        ident = Identifier('drop', slash=True)
        self.assertEqual('/drop', str(ident))

    def test_eof(self):
        s = Stream('')
        tok = next_token(s)
        self.assertIsInstance(tok, Error)
        self.assertEqual(tok.got, 'EOF')

    def test_punctuation(self):
        s = Stream('( , )')
        tok = next_token(s)
        self.assertIsInstance(tok, LParen)
        tok = next_token(s)
        self.assertIsInstance(tok, Comma)
        tok = next_token(s)
        self.assertIsInstance(tok, RParen)
        tok = next_token(s)
        self.assertIsInstance(tok, Error)

    def test_more_identifiers(self):
        s = Stream('/create table if not exists /students /drop')
        n = lambda: next_token(s)

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
        tok = next_token(s)
        self.assertIsInstance(tok, Integer)
        self.assertEqual(42, tok.value)
        tok = next_token(s)
        self.assertIsInstance(tok, Float)
        self.assertAlmostEqual(15.37, tok.value, 2)
        tok = next_token(s)
        self.assertIsInstance(tok, String)
        self.assertEqual('UFO', tok.value)

        s = Stream(' \'not the...')
        tok = next_token(s)
        self.assertIsInstance(tok, Error)

        s = Stream(" 'abc\\' def' ")
        tok = next_token(s)
        self.assertEqual(tok, String("abc' def"))

    def test_comment(self):
        s = Stream('42, -- this is the answer\n'
                   '37  -- while this one is definitely not.\n')
        n = lambda: next_token(s)
        tok = (n(), n(), n(), n())
        self.assertEqual(tok[0], Integer(42))
        self.assertIsInstance(tok[1], Comma)
        self.assertEqual(tok[2], Integer(37))
        self.assertIsInstance(tok[3], Error)

    def test_operators(self):
        s = Stream(
            '  *    >=   >    /=   /    /5        /and')
        n = lambda: next_token(s)

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
        n = lambda: next_token(s)

        tok = (n(), n(), n(), n())
        self.assertEqual(tok[0], Placeholder(1))
        self.assertIsInstance(tok[1], Comma)
        self.assertEqual(tok[2], Placeholder(32))
        self.assertIsInstance(tok[3], Error)

    def test_all_keywords(self):
        # @formatter:off
        self.assertIsInstance(next_token(Stream('and')),        Operator)
        self.assertIsInstance(next_token(Stream('as')),         As)
        self.assertIsInstance(next_token(Stream('create')),     Create)
        self.assertIsInstance(next_token(Stream('delete')),     Delete)
        self.assertIsInstance(next_token(Stream('drop')),       Drop)
        self.assertIsInstance(next_token(Stream('exists')),     Exists)
        self.assertIsInstance(next_token(Stream('float')),      Identifier)
        self.assertIsInstance(next_token(Stream('from')),       From)
        self.assertIsInstance(next_token(Stream('if')),         If)
        self.assertIsInstance(next_token(Stream('insert')),     Insert)
        self.assertIsInstance(next_token(Stream('integer')),    Identifier)
        self.assertIsInstance(next_token(Stream('into')),       Into)
        self.assertIsInstance(next_token(Stream('join')),       Join)
        self.assertIsInstance(next_token(Stream('key')),        Key)
        self.assertIsInstance(next_token(Stream('not')),        Not)
        self.assertIsInstance(next_token(Stream('on')),         On)
        self.assertIsInstance(next_token(Stream('or')),         Operator)
        self.assertIsInstance(next_token(Stream('primary')),    Primary)
        self.assertIsInstance(next_token(Stream('select')),     Select)
        self.assertIsInstance(next_token(Stream('set')),        Set)
        self.assertIsInstance(next_token(Stream('table')),      Table)
        self.assertIsInstance(next_token(Stream('update')),     Update)
        self.assertIsInstance(next_token(Stream('values')),     Values)
        self.assertIsInstance(next_token(Stream('varchar')),    Identifier)
        self.assertIsInstance(next_token(Stream('where')),      Where)
        # @formatter:on
