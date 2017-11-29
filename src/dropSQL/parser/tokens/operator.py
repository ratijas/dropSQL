from .token import Token


class Operator(Token):
    EQ = '='
    NE = '/='
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    GT = '>'
    LT = '<'
    GE = '>='
    LE = '<='

    AND = '/and'
    OR = '/or'

    def __init__(self, operator: str) -> None:
        super().__init__()

        self.operator = operator

    def __repr__(self) -> str:
        return f'Operator({self.operator})'

    def __eq__(self, o: object) -> bool:
        return isinstance(o, Operator) and self.operator == o.operator
