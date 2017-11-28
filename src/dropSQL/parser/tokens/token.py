import abc


class Token(metaclass=abc.ABCMeta):
    """
    enum Token.
    """

    def __repr__(self) -> str:
        return f'Token({self.__class__.__name__})'
