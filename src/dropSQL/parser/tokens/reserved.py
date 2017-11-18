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


class As(Reserved):
    def __init__(self) -> None:
        super().__init__('as', True)


class Create(Reserved):
    def __init__(self) -> None:
        super().__init__('create', True)


class Drop(Reserved):
    def __init__(self) -> None:
        super().__init__('drop', True)


class Delete(Reserved):
    def __init__(self) -> None:
        super().__init__('delete', True)


class Select(Reserved):
    def __init__(self) -> None:
        super().__init__('select', True)


class From(Reserved):
    def __init__(self) -> None:
        super().__init__('from', False)


class Join(Reserved):
    def __init__(self) -> None:
        super().__init__('join', True)


class On(Reserved):
    def __init__(self) -> None:
        super().__init__('on', True)


class Table(Reserved):
    def __init__(self) -> None:
        super().__init__('table', False)


class If(Reserved):
    def __init__(self) -> None:
        super().__init__('if', False)


class Not(Reserved):
    def __init__(self) -> None:
        super().__init__('not', False)


class Exists(Reserved):
    def __init__(self) -> None:
        super().__init__('exists', False)


class Primary(Reserved):
    def __init__(self) -> None:
        super().__init__('primary', True)


class Key(Reserved):
    def __init__(self) -> None:
        super().__init__('key', False)


class Insert(Reserved):
    def __init__(self) -> None:
        super().__init__('insert', True)


class Into(Reserved):
    def __init__(self) -> None:
        super().__init__('into', False)


class Update(Reserved):
    def __init__(self) -> None:
        super().__init__('update', True)


class Set(Reserved):
    def __init__(self) -> None:
        super().__init__('set', True)


class Values(Reserved):
    def __init__(self) -> None:
        super().__init__('values', False)


class Where(Reserved):
    def __init__(self) -> None:
        super().__init__('where', True)
