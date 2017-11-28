import abc


class Ast(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def to_sql(self) -> str:
        """
        Like __str__, but explicitly states its purpose

        :return: Serialized statement.
        """


class AstStmt(Ast, metaclass=abc.ABCMeta):
    """
    Statement mix-in for Ast subclasses
    """
