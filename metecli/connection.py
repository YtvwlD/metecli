import requests
from requests.exceptions import ConnectionError
from urllib.parse import urljoin

import logging
log = logging.getLogger(__name__)

class Connection():
    def __init__(self, base_url=None):
        self._base_url = base_url
    
    def users(self):
        """Lists all users."""
        r = requests.get(urljoin(self._base_url, "/users.json"))
        return r.json()
    
    def get_user(self, uid):
        """Get information about a user."""
        r = requests.get(urljoin(self._base_url, "/users/{}.json".format(uid)))
        return r.json()
    
    def buy(self, uid, did):
        """Buy a drink."""
        r = requests.get(urljoin(self._base_url, "/users/{}/buy.json?drink={}".format(uid, did)))
        assert r.ok
    
    def pay(self, uid, amount):
        """Pay an amount."""
        r = requests.get(urljoin(self._base_url, "/users/{}/payment.json?amount={}".format(uid, amount))) # TODO: pay.json
        print(r.text)
        assert r.ok
    
    def deposit(self, uid, amount):
        """Deposit money."""
        r = requests.get(urljoin(self._base_url, "/users/{}/deposit.json?amount={}".format(uid, amount)))
        print(r.text)
        assert r.ok
    
    def drinks(self):
        """Lists all drinks."""
        r = requests.get(urljoin(self._base_url, "/drinks.json"))
        return r.json()
    
    def try_connect(self):
        """Tries to connect to the server."""
        try:
            self.users()
            return True
        except ConnectionError:
            return False
        
