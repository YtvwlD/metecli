from ..config import Config
from ..connection import Connection
from ..models import AuditInfo, Barcode, Drink, ServerInfo, User

from requests import Session
from urllib.parse import urljoin
from datetime import date
from typing import Optional, List, Tuple

import logging
log = logging.getLogger(__name__)


class ApiV2(Connection):
    def __init__(
        self, sess: Session, conf: Optional['Config'], base_url: str,
    ) -> None:
        self._sess = sess
        self._conf = conf
        self._base_url = base_url
    
    def server_info(self) -> ServerInfo:
        """Get information about the server."""
        r = self._sess.get(urljoin(self._base_url, "info.json"))
        r.raise_for_status()
        return ServerInfo.from_v2(r.json())
    
    def users(self) -> List[User]:
        """Lists all users."""
        r = self._sess.get(urljoin(self._base_url, "users.json"))
        r.raise_for_status()
        return [User.from_v2(u) for u in r.json()]
    
    def audits(
        self, user: Optional[int] = None, from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> AuditInfo:
        """Get audits."""
        params = dict()
        if user:
            assert isinstance(user, int)
            params["user"] = user
        if from_date:
            params["start_date[year]"] = from_date.year
            params["start_date[month]"] = from_date.month
            params["start_date[day]"] = from_date.day
        if to_date:
            params["end_date[year]"] = to_date.year
            params["end_date[month]"] = to_date.month
            params["end_date[day]"] = to_date.day
        r = self._sess.get(
            urljoin(self._base_url, "audits.json"), params=params,
        )
        r.raise_for_status()
        return AuditInfo.from_v2(r.json())
    
    def get_user(self, uid: int) -> User:
        """Get information about a user."""
        r = self._sess.get(
            urljoin(self._base_url, "users/{}.json".format(uid)),
        )
        r.raise_for_status()
        return User.from_v2(r.json())
    
    def modify_user(self, user: User) -> None:
        """Modifys an existing user."""
        r = self._sess.patch(
            urljoin(self._base_url, "users/{}.json").format(user.id),
            json=user.to_v2(),
        )
        r.raise_for_status()
    
    def delete_user(self, uid: int) -> None:
        r = self._sess.delete(
            urljoin(self._base_url, "users/{}.json".format(uid)),
        )
        r.raise_for_status()
    
    def get_user_defaults(self) -> User:
        """Gets the default settings for creating a new user."""
        log.warn("This server does not let us know of its defaults for creating new users. Using our own.")
        return User(
            id=None, name="", email=None, balance=0.0,
            active=True, audit=False, redirect=True,
        )
    
    def add_user(self, user: User) -> User:
        """Creates a new user."""
        r = self._sess.post(
            urljoin(self._base_url, "users.json"), json=user.to_v2(),
        )
        r.raise_for_status()
        return User.from_v2(r.json())
    
    def buy(self, uid: int, did: int) -> None:
        """Buy a drink."""
        r = self._sess.post(urljoin(
            self._base_url, "users/{}/product.json".format(uid)),
            json={"product": did},
        )
        r.raise_for_status()
    
    def pay(self, uid: int, amount: float) -> None:
        """Pay an amount."""
        r = self._sess.post(
            urljoin(self._base_url, "users/{}/pay.json".format(uid)),
            json={"amount": int(amount * 100)},
        )
        r.raise_for_status()
    
    def deposit(self, uid: int, amount: float) -> None:
        """Deposit money."""
        r = self._sess.post(
            urljoin(self._base_url, "users/{}/deposit.json".format(uid)),
            json={"amount": int(amount * 100)},
        )
        r.raise_for_status()
    
    def transfer(self, sender: int, receiver: int, amount: float) -> None:
        """Transfer money."""
        log.warn("This feature isn't really supported by the server. Use it with caution.")
        self.pay(sender, amount)
        self.deposit(receiver, amount)
    
    def drinks(self) -> List[Drink]:
        """Lists all drinks."""
        r = self._sess.get(urljoin(self._base_url, "products.json"))
        r.raise_for_status()
        return [Drink.from_v2(d) for d in r.json()]
    
    def modify_drink(self, drink: Drink) -> None:
        """Modifys an existing drink."""
        r = self._sess.patch(
            urljoin(self._base_url, "products/{}.json").format(drink.id),
            json=drink.to_v2(),
        )
        r.raise_for_status()
    
    def get_drink_defaults(self) -> Drink:
        """Gets the default settings for creating a new drink."""
        log.warn("This server does not let us know of its defaults for creating new drinks. Using our own.")
        return Drink(
            id=None, name="", bottle_size=None, caffeine=None,
            price=1.5, active=True,
        )
    
    def create_drink(self, drink: Drink) -> Drink:
        """Creates a new drink."""
        r = self._sess.post(
            urljoin(self._base_url, "products.json"),
            json=drink.to_v2()
        )
        r.raise_for_status()
        return Drink.from_v2(r.json())
    
    def delete_drink(self, drink_id: int) -> None:
        """Deletes an existing drink."""
        r = self._sess.delete(
            urljoin(self._base_url, "products/{}.json").format(drink_id)
        )
        r.raise_for_status()
    
    def barcodes(self) -> List[Barcode]:
        """Lists all barcodes."""
        raise NotImplementedError
    
    def get_barcode_defaults(self) -> Barcode:
        """Get the defaults for creating new barcodes."""
        raise NotImplementedError
    
    def create_barcode(self, barcode: Barcode) -> Barcode:
        """Creates a new barcode."""
        raise NotImplementedError
    
    def delete_barcode(self, barcode_id: int) -> None:
        """Delete a barcode."""
        raise NotImplementedError
    
    def try_connect(self) -> bool:
        """Tries to connect to the server."""
        try:
            self.server_info()
            return True
        except Exception as exc:
            log.error("%s: %s", type(exc).__name__, exc)
            return False
    
    def api_version(self) -> str:
        """Get the API version."""
        return "v2"
    
    def _try_upgrade(self) -> Tuple[bool, 'Connection']:
        """Try to upgrade the API version.
        
        Return whether a change occurred and the new API handle."""
        return (False, self)  # TODO