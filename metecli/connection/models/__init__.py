from typing import Literal

from .audit import Audit, AuditInfo
from .barcode import Barcode
from .drink import Drink
from .server_info import ServerInfo
from .user import User

ApiVersion = Literal["legacy", "v1", "v2", "v3"]
