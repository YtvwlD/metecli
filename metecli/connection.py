# from .config import Config (moved to bottom)
# from .utils import Thing (moved to bottom)

from requests import Session
from urllib.parse import urljoin
from datetime import datetime
from typing import Optional, List, Dict

import logging
log = logging.getLogger(__name__)

class Connection():
    def __init__(self, config: Optional['Config'], base_url: Optional[str] = None) -> None:
        self._sess = Session()
        if config and not base_url:
            self._conf = config
            if not config["connection"]["base_url"]:
                raise Exception("The connection is not configured yet.")
            self._base_url = config["connection"]["base_url"]
            if not config["connection"]["api_version"]:
                raise Exception("The configured connection doesn't have api_version set.")
            self._api_version = config["connection"]["api_version"]
            assert self._api_version in ("legacy", "v1")
            self._try_upgrade()
        elif base_url and not config:
            self._conf = None
            self._base_url = base_url
            self._api_version = self.determine_api_version()
        else:
            raise Exception("Either config *or* base_url must be provided.")
    
    def users(self) -> List['Thing']:
        """Lists all users."""
        r = self._sess.get(urljoin(self._base_url, "users.json"))
        r.raise_for_status()
        return r.json()
    
    def audits(self, user: Optional[int] = None, from_date: Optional[datetime] = None, to_date: Optional[datetime] = None) -> Dict[str, object]:
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
        r = self._sess.get(urljoin(self._base_url, "audits.json"), params=params)
        r.raise_for_status()
        return r.json()
    
    def get_user(self, uid: int) -> 'Thing':
        """Get information about a user."""
        r = self._sess.get(urljoin(self._base_url, "users/{}.json".format(uid)))
        r.raise_for_status()
        return r.json()
    
    def modify_user(self, user: 'Thing') -> None:
        """Modifys an existing user."""
        r = self._sess.patch(urljoin(self._base_url, "users/{}.json").format(user["id"]), json=user)
        r.raise_for_status()
    
    def delete_user(self, uid: int) -> None:
        r = self._sess.delete(urljoin(self._base_url, "users/{}.json".format(uid)))
        r.raise_for_status()
    
    def get_user_defaults(self) -> 'Thing':
        """Gets the default settings for creating a new user."""
        r = self._sess.get(urljoin(self._base_url, "users/new.json"))
        r.raise_for_status()
        return r.json()
    
    def add_user(self, user: 'Thing') -> 'Thing':
        """Creates a new user."""
        r = self._sess.post(urljoin(self._base_url, "users.json"), json=user)
        r.raise_for_status()
        return r.json()
    
    def buy(self, uid: int, did: int) -> None:
        """Buy a drink."""
        r = self._sess.get(urljoin(self._base_url, "users/{}/buy.json?drink={}".format(uid, did)))
        r.raise_for_status()
    
    def pay(self, uid: int, amount: float) -> None:
        """Pay an amount."""
        r = self._sess.get(urljoin(self._base_url, "users/{}/payment.json?amount={}".format(uid, amount)))
        r.raise_for_status()
    
    def deposit(self, uid: int, amount: float) -> None:
        """Deposit money."""
        r = self._sess.get(urljoin(self._base_url, "users/{}/deposit.json?amount={}".format(uid, amount)))
        r.raise_for_status()
    
    def transfer(self, sender: int, receiver: int, amount: float) -> None:
        """Transfer money."""
        log.warning("This feature isn't really supported by the server. Use it with caution.")
        self.pay(sender, amount)
        self.deposit(receiver, amount)
    
    def drinks(self) -> List['Thing']:
        """Lists all drinks."""
        r = self._sess.get(urljoin(self._base_url, "drinks.json"))
        r.raise_for_status()
        return r.json()
    
    def modify_drink(self, drink: 'Thing') -> None:
        """Modifys an existing drink."""
        r = self._sess.patch(urljoin(self._base_url, "drinks/{}.json").format(drink["id"]), json=drink)
        r.raise_for_status()
    
    def get_drink_defaults(self) -> 'Thing':
        """Gets the default settings for creating a new drink."""
        r = self._sess.get(urljoin(self._base_url, "drinks/new.json"))
        r.raise_for_status()
        return r.json()
    
    def create_drink(self, drink: 'Thing') -> 'Thing':
        """Creates a new drink."""
        r = self._sess.post(urljoin(self._base_url, "drinks.json"), json=drink)
        r.raise_for_status()
        return r.json()
    
    def delete_drink(self, drink_id: int) -> None:
        """Deletes an existing drink."""
        r = self._sess.delete(urljoin(self._base_url, "drinks/{}.json").format(drink_id))
        r.raise_for_status()
    
    def barcodes(self) -> List['Thing']:
        """Lists all barcodes."""
        r = self._sess.get(urljoin(self._base_url, "barcodes.json"))
        return r.json()
    
    def get_barcode_defaults(self) -> 'Thing':
        """Get the defaults for creating new barcodes."""
        r = self._sess.get(urljoin(self._base_url, "barcodes/new.json"))
        r.raise_for_status()
        return r.json()
    
    def create_barcode(self, barcode: 'Thing') -> 'Thing':
        """Creates a new barcode."""
        r = self._sess.post(urljoin(self._base_url, "barcodes.json"), json=barcode)
        r.raise_for_status()
        return r.json()
    
    def delete_barcode(self, barcode_id: int) -> None:
        """Delete a barcode."""
        r = self._sess.delete(urljoin(self._base_url, "barcodes/{}.json").format(barcode_id))
        r.raise_for_status()
    
    def try_connect(self) -> bool:
        """Tries to connect to the server."""
        try:
            self.users()
            return True
        except Exception as exc:
            log.error("%s: %s", type(exc).__name__, exc)
            return False
    
    def determine_api_version(self) -> str:
        """Tries to determine the API version."""
        if "api/v1" in self._base_url:
            return "v1"
        else:
            return "legacy"
    
    def _try_upgrade(self) -> None:
        """Tries to upgrade the API version."""
        changed = False
        for upgrade in (("legacy", "v1"),): # What should be upgraded?
            if self._api_version != upgrade[0]:
                continue
            log.info("Trying to upgrade the API version from '%s' to '%s'...", upgrade[0], upgrade[1])
            # save the old values
            old_base_url = self._base_url
            self._api_version = upgrade[1]
            try:
                if upgrade == ("legacy", "v1"): # try legacy -> v1
                    self._base_url = urljoin(self._base_url, "api/v1/")
                    assert self.try_connect()
                    changed = True
            except:
                # something went wrong
                log.warning("The server doesn't support API version '%s'. (Or the connection failed.)", upgrade[1])
                # restore the old values
                self._api_version = upgrade[0]
                self._base_url = old_base_url
        if changed and self._conf:
            # save the new values
            self._conf["connection"]["api_version"] = self._api_version
            self._conf["connection"]["base_url"] = self._base_url
            self._conf.save()

from .config import Config
from .utils import Thing
