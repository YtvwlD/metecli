import requests
from requests.exceptions import ConnectionError
from urllib.parse import urljoin

class Connection():
    def __init__(self, log=None, base_url=None):
        self._log = log
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
        
