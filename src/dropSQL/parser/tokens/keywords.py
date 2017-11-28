from .identifier import Keyword

__all__ = [
    'As',
    'Create',
    'Delete',
    'Drop',
    'Exists',
    'From',
    'If',
    'Insert',
    'Into',
    'Join',
    'Key',
    'Not',
    'On',
    'Primary',
    'Select',
    'SetKw',
    'Table',
    'Update',
    'Values',
    'Where',
]


class As(Keyword):
    def __init__(self) -> None:
        super().__init__('as', True)


class Create(Keyword):
    def __init__(self) -> None:
        super().__init__('create', True)


class Drop(Keyword):
    def __init__(self) -> None:
        super().__init__('drop', True)


class Delete(Keyword):
    def __init__(self) -> None:
        super().__init__('delete', True)


class Select(Keyword):
    def __init__(self) -> None:
        super().__init__('select', True)


class From(Keyword):
    def __init__(self) -> None:
        super().__init__('from', False)


class Join(Keyword):
    def __init__(self) -> None:
        super().__init__('join', True)


class On(Keyword):
    def __init__(self) -> None:
        super().__init__('on', True)


class Table(Keyword):
    def __init__(self) -> None:
        super().__init__('table', False)


class If(Keyword):
    def __init__(self) -> None:
        super().__init__('if', False)


class Not(Keyword):
    def __init__(self) -> None:
        super().__init__('not', False)


class Exists(Keyword):
    def __init__(self) -> None:
        super().__init__('exists', False)


class Primary(Keyword):
    def __init__(self) -> None:
        super().__init__('primary', True)


class Key(Keyword):
    def __init__(self) -> None:
        super().__init__('key', False)


class Insert(Keyword):
    def __init__(self) -> None:
        super().__init__('insert', True)


class Into(Keyword):
    def __init__(self) -> None:
        super().__init__('into', False)


class Update(Keyword):
    def __init__(self) -> None:
        super().__init__('update', True)


class SetKw(Keyword):
    def __init__(self) -> None:
        super().__init__('set', True)


class Values(Keyword):
    def __init__(self) -> None:
        super().__init__('values', False)


class Where(Keyword):
    def __init__(self) -> None:
        super().__init__('where', True)
