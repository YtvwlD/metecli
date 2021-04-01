from enum import Enum, unique


@unique
class ApiVersion(Enum):
    legacy = 1
    v1 = 2
    # TODO