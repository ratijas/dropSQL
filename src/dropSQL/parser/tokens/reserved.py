from . import *

__all__ = (
    'As',
    'Create',
    'Drop',
    'Delete',
    'Select',
    'From',
    'Join',
    'On',
    'Table',
    'If',
    'Not',
    'Exists',
    'Primary',
    'Key',
    'Insert',
    'Into',
    'Update',
    'Set',
    'Values',
    'Where',
)


class As(Identifier):
    def __init__(self) -> None:
        super().__init__('as', True)


class Create(Identifier):
    def __init__(self) -> None:
        super().__init__('create', True)


class Drop(Identifier):
    def __init__(self) -> None:
        super().__init__('drop', True)


class Delete(Identifier):
    def __init__(self) -> None:
        super().__init__('delete', True)


class Select(Identifier):
    def __init__(self) -> None:
        super().__init__('select', True)


class From(Identifier):
    def __init__(self) -> None:
        super().__init__('from', False)


class Join(Identifier):
    def __init__(self) -> None:
        super().__init__('join', True)


class On(Identifier):
    def __init__(self) -> None:
        super().__init__('on', True)


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


class Update(Identifier):
    def __init__(self) -> None:
        super().__init__('update', True)


class Set(Identifier):
    def __init__(self) -> None:
        super().__init__('set', True)


class Values(Identifier):
    def __init__(self) -> None:
        super().__init__('values', False)


class Where(Identifier):
    def __init__(self) -> None:
        super().__init__('where', True)
