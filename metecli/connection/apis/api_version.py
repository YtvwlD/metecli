from enum import Enum, unique


@unique
class ApiVersion(Enum):
    legacy = 0
    v1 = 1
    v2 = 2
    v3 = 3
    # TODO