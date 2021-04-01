from .config import Config
from .models import AuditInfo, Barcode, Drink, User

from abc import ABCMeta, abstractmethod
from requests import Session
from datetime import date
from typing import Optional, List, Dict, Tuple

import logging
log = logging.getLogger(__name__)


class Connection(metaclass=ABCMeta):
    @classmethod
    def new(
        cls, config: Optional['Config'], base_url: Optional[str] = None
    ) -> None:
        sess = Session()
        if config and not base_url:
            if not config["base_url"]:
                raise Exception("The connection is not configured yet.")
            base_url = config["base_url"]
            if not config["api_version"]:
                raise Exception("The configured connection doesn't have api_version set.")
            api_version = config["api_version"]
        elif base_url and not config:
            api_version = cls.determine_api_version(base_url)
        else:
            raise Exception("Either config *or* base_url must be provided.")
        if api_version in ("legacy", "v1"):
            from .apis.apiv1 import ApiV1
            return ApiV1(sess, config, base_url, api_version)
        else:
            raise NotImplementedError("This API version is not supported (yet).")
    
    @abstractmethod
    def users(self) -> List[User]:
        """Lists all users."""
        pass
    
    @abstractmethod
    def audits(
        self, user: Optional[int] = None, from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> AuditInfo:
        """Get audits."""
        pass
    
    @abstractmethod
    def get_user(self, uid: int) -> User:
        """Get information about a user."""
        pass
    
    @abstractmethod
    def modify_user(self, user: User) -> None:
        """Modifys an existing user."""
        pass
    
    @abstractmethod
    def delete_user(self, uid: int) -> None:
        pass
    
    @abstractmethod
    def get_user_defaults(self) -> User:
        """Gets the default settings for creating a new user."""
        pass
    
    @abstractmethod
    def add_user(self, user: User) -> User:
        """Creates a new user."""
        pass
    
    @abstractmethod
    def buy(self, uid: int, did: int) -> None:
        """Buy a drink."""
        pass
    
    @abstractmethod
    def pay(self, uid: int, amount: float) -> None:
        """Pay an amount."""
        pass
    
    @abstractmethod
    def deposit(self, uid: int, amount: float) -> None:
        """Deposit money."""
        pass
    
    @abstractmethod
    def transfer(self, sender: int, receiver: int, amount: float) -> None:
        """Transfer money."""
        pass
    
    @abstractmethod
    def drinks(self) -> List[Drink]:
        """Lists all drinks."""
        pass
    
    @abstractmethod
    def modify_drink(self, drink: Drink) -> None:
        """Modifys an existing drink."""
        pass
    
    @abstractmethod
    def get_drink_defaults(self) -> Drink:
        """Gets the default settings for creating a new drink."""
        pass
    
    @abstractmethod
    def create_drink(self, drink: Drink) -> Drink:
        """Creates a new drink."""
        pass
    
    @abstractmethod
    def delete_drink(self, drink_id: int) -> None:
        """Deletes an existing drink."""
        pass
    
    @abstractmethod
    def barcodes(self) -> List[Barcode]:
        """Lists all barcodes."""
        pass
    
    @abstractmethod
    def get_barcode_defaults(self) -> Barcode:
        """Get the defaults for creating new barcodes."""
        pass
    
    @abstractmethod
    def create_barcode(self, barcode: Barcode) -> Barcode:
        """Creates a new barcode."""
        pass
    
    @abstractmethod
    def delete_barcode(self, barcode_id: int) -> None:
        """Delete a barcode."""
        pass
    
    @abstractmethod
    def try_connect(self) -> bool:
        """Tries to connect to the server."""
        pass
    
    @classmethod
    def determine_api_version(cls, base_url: str) -> str:
        """Tries to determine the API version."""
        if "api/v1" in base_url:
            return "v1"
        else:
            return "legacy"
        # TODO
    
    def try_upgrade(self) -> 'Connection':
        """Tries to upgrade the API version."""
        changed, new_conn = self._try_upgrade()
        if changed and self._conf:
            # save the new values
            self._conf["api_version"] = self._api_version
            self._conf["base_url"] = self._base_url
            self._conf.save()
        return new_conn
    
    @abstractmethod
    def _try_upgrade(self) -> Tuple[bool, 'Connection']:
        """Try to upgrade the API version.
        
        Return whether a change occurred and the new API handle."""
        pass
