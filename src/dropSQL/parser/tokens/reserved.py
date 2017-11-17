from . import *

__all__ = (
    'Create',
    'Drop',
    'Table',
    'If',
    'Not',
    'Exists',
    'Values',
    'Primary',
    'Key',
    'Insert',
    'Into',
)


class Create(Identifier):
    def __init__(self) -> None:
        super().__init__('create', True)


class Drop(Identifier):
    def __init__(self) -> None:
        super().__init__('drop', True)


class Table(Identifier):
    def __init__(self) -> None:
        super().__init__('table', False)


class If(Identifier):
    def __init__(self) -> None:
        super().__init__('if', False)


class Not(Identifier):
    def __init__(self) -> None:
        super().__init__('not', False)


class Exists(Identifier):
    def __init__(self) -> None:
        super().__init__('exists', False)


class Primary(Identifier):
    def __init__(self) -> None:
        super().__init__('primary', True)


class Key(Identifier):
    def __init__(self) -> None:
        super().__init__('key', False)


class Insert(Identifier):
    def __init__(self) -> None:
        super().__init__('insert', True)


class Into(Identifier):
    def __init__(self) -> None:
        super().__init__('into', False)


class Values(Identifier):
    def __init__(self) -> None:
        super().__init__('values', False)
