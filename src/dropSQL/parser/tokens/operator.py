from . import *


class Operator(Token):
    def __init__(self, operator: str) -> None:
        super().__init__()

        self.operator = operator

    def __eq__(self, o: 'Operator') -> bool:
        return isinstance(o, Operator) and self.operator == o.operator
