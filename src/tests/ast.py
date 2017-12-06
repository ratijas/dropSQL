from unittest import TestCase

from dropSQL.ast import *
from dropSQL.parser.tokens import *


class AstTestCase(TestCase):
    def test_expression(self):
        self.assertEqual('42', ExpressionLiteralInt(42).to_sql())
        self.assertEqual('42.000000', ExpressionLiteralFloat(42.0).to_sql())
        self.assertEqual("'world'", ExpressionLiteralVarChar('world').to_sql())
        self.assertEqual(r"'ab\\cd\'s'", ExpressionLiteralVarChar(r"ab\cd's").to_sql())
        self.assertEqual('?42', ExpressionPlaceholder(42).to_sql())
        self.assertEqual('name', ExpressionReference(None, Identifier('name')).to_sql())
        self.assertEqual('person name', ExpressionReference(Identifier('person'), Identifier('name')).to_sql())
        self.assertEqual('person/name', ExpressionReference(Identifier('person'), Identifier('name', True)).to_sql())
        self.assertEqual('(2 + 3) = 5',
                         ExpressionBinary(
                             Operator('='),
                             ExpressionParen(
                                 ExpressionBinary(
                                     Operator('+'),
                                     ExpressionLiteralInt(2),
                                     ExpressionLiteralInt(3))),
                             ExpressionLiteralInt(5))
                         .to_sql())

    def test_aliased(self):
        self.assertEqual('person', AliasedTable(Identifier('person')).to_sql())
        self.assertEqual('person p', AliasedTable(Identifier('person'), Identifier('p')).to_sql())
        self.assertEqual('height / 3 /as /h3',
                         AliasedExpression(
                             ExpressionBinary(
                                 Operator('/'),
                                 ExpressionReference(None, Identifier('height')),
                                 ExpressionLiteralInt(3),
                             ), Identifier('h3', True))
                         .to_sql())

    def test_types(self):
        self.assertEqual('float', FloatTy().to_sql())
        self.assertEqual('integer', IntegerTy().to_sql())
        self.assertEqual('varchar(42)', VarCharTy(42).to_sql())

    def test_column_def(self):
        self.assertEqual('/name varchar(42) /primary key',
                         ColumnDef(Identifier('name', True), VarCharTy(42), True).to_sql())
        self.assertEqual('age integer',
                         ColumnDef(Identifier('age', False), IntegerTy(), False).to_sql())
        self.assertEqual('height float',
                         ColumnDef(Identifier('height', False), FloatTy(), False).to_sql())

    def test_result_column(self):
        self.assertEqual('*', ResultStar().to_sql())
        self.assertEqual('name /as n',
                         ResultExpression(
                             AliasedExpression(
                                 ExpressionReference(table=None, column=Identifier('name')),
                                 Identifier('n')))
                         .to_sql())

    def test_create_table(self):
        ct = CreateTable(IfNotExists(), Identifier('person', True), [
            ColumnDef(Identifier('name', False), VarCharTy(42), True),
            ColumnDef(Identifier('age', True), IntegerTy(), False),
            ColumnDef(Identifier('height', False), FloatTy(), False),
        ])
        sql = ct.to_sql()
        expected = (
            '/create table if not exists /person (\n'
            '\tname varchar(42) /primary key,\n'
            '\t/age integer,\n'
            '\theight float,\n'
            ') /drop'
        )
        self.assertEqual(expected, sql)

    def test_drop_table(self):
        dt = DropTable(IfExists(), Identifier('score', True))
        sql = dt.to_sql()
        expected = '/drop table if exists /score /drop'
        self.assertEqual(expected, sql)

    def test_insert_into(self):
        ii = InsertInto(
            Identifier('person', True),
            [
                Identifier('name', False),
                Identifier('age', True),
                Identifier('height', False),
            ],
            [
                [ExpressionLiteralVarChar('morty'), ExpressionLiteralInt(11), ExpressionPlaceholder(1)],
                [ExpressionLiteralVarChar('jimmy'), ExpressionLiteralInt(10), ExpressionPlaceholder(2)],
                [ExpressionLiteralVarChar('jerry'),
                 ExpressionBinary(
                     Operator('+'),
                     ExpressionLiteralInt(14),
                     ExpressionLiteralInt(16)),
                 ExpressionParen(ExpressionLiteralFloat(180.42))],
            ]
        )
        sql = ii.to_sql()
        expected = (
            "/insert into /person (name, /age, height) values "
            "('morty', 11, ?1), "
            "('jimmy', 10, ?2), "
            "('jerry', 14 + 16, (180.420000)) "
            "/drop"
        )
        self.assertEqual(expected, sql)

    def test_delete_from(self):
        self.assertEqual("/delete from /person /where name = 'morty' /drop",
                         DeleteFrom(
                             Identifier('person', True),
                             ExpressionBinary(
                                 Operator('='),
                                 ExpressionReference(None, Identifier('name')),
                                 ExpressionLiteralVarChar('morty')))
                         .to_sql())

    def test_update_set(self):
        self.assertEqual('/update /person /set name = ?1, age = ?2 /where height > 100 /drop',
                         UpdateSet(
                             Identifier('person', True),
                             [
                                 (Identifier('name'), ExpressionPlaceholder(1)),
                                 (Identifier('age'), ExpressionPlaceholder(2)),
                             ],
                             ExpressionBinary(
                                 Operator('>'),
                                 ExpressionReference(None, Identifier('height')),
                                 ExpressionLiteralInt(100)))
                         .to_sql())

    def test_select_from(self):
        self.assertEqual('/select P/name /as first_name, * /from person P /drop',
                         SelectFrom(
                             columns=[
                                 ResultExpression(
                                     AliasedExpression(
                                         ExpressionReference(
                                             Identifier('P'),
                                             Identifier('name', True)),
                                         Identifier('first_name'))),
                                 ResultStar(),
                             ],
                             table=AliasedTable(Identifier('person'), Identifier('P')))
                         .to_sql())

        self.assertEqual(
            '/select * /from person P, department D /join manager M /on M/department_id = D/id /drop',
            SelectFrom(
                columns=[ResultStar()],
                table=AliasedTable(Identifier('person'), Identifier('P')),
                joins=[
                    CrossJoin(AliasedTable(Identifier('department'), Identifier('D'))),
                    InnerJoin(AliasedTable(Identifier('manager'), Identifier('M')),
                              ExpressionBinary(
                                  Operator('='),
                                  ExpressionReference(Identifier('M'), Identifier('department_id', True)),
                                  ExpressionReference(Identifier('D'), Identifier('id', True)))),
                ]).to_sql())

        self.assertEqual('/select * /from person P /where P/age >= 18 /drop',
                         SelectFrom(
                             columns=[ResultStar()],
                             table=AliasedTable(Identifier('person'), Identifier('P')),
                             where=ExpressionBinary(
                                 Operator('>='),
                                 ExpressionReference(Identifier('P'), Identifier('age', True)),
                                 ExpressionLiteralInt(18)))
                         .to_sql())
