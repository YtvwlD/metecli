import requests
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
    
    def audits(self, user=None, from_date=None, to_date=None):
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
        r = requests.get(urljoin(self._base_url, "/audits.json"), params=params)
        return r.json()
    
    def get_user(self, uid):
        """Get information about a user."""
        r = requests.get(urljoin(self._base_url, "/users/{}.json".format(uid)))
        return r.json()
    
    def modify_user(self, user):
        """Modifys an existing user."""
        r = requests.patch(urljoin(self._base_url, "/users/{}.json").format(user["id"]), json=user)
        assert r.ok
    
    def delete_user(self, uid):
        r = requests.delete(urljoin(self._base_url, "/users/{}.json".format(uid)))
        assert r.ok
    
    def get_user_defaults(self):
        """Gets the default settings for creating a new user."""
        r = requests.get(urljoin(self._base_url, "/users/new.json"))
        return r.json()
    
    def add_user(self, user):
        """Creates a new user."""
        r = requests.post(urljoin(self._base_url, "/users.json"), json=user)
        return r.json()
    
    def buy(self, uid, did):
        """Buy a drink."""
        r = requests.get(urljoin(self._base_url, "/users/{}/buy.json?drink={}".format(uid, did)))
        assert r.ok
    
    def pay(self, uid, amount):
        """Pay an amount."""
        r = requests.get(urljoin(self._base_url, "/users/{}/payment.json?amount={}".format(uid, amount)))
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
    
    def modify_drink(self, drink):
        """Modifys an existing drink."""
        r = requests.patch(urljoin(self._base_url, "/drinks/{}.json").format(drink["id"]), json=drink)
        assert r.ok
    
    def get_drink_defaults(self):
        """Gets the default settings for creating a new drink."""
        r = requests.get(urljoin(self._base_url, "/drinks/new.json"))
        return r.json()
    
    def create_drink(self, drink):
        """Creates a new drink."""
        r = requests.post(urljoin(self._base_url, "/drinks.json"), json=drink)
        return r.json()
    
    def delete_drink(self, drink_id):
        """Deletes an existing drink."""
        r = requests.delete(urljoin(self._base_url, "/drinks/{}.json").format(drink_id))
        assert r.ok
    
    def barcodes(self):
        """Lists all barcodes."""
        r = requests.get(urljoin(self._base_url, "/barcodes.json"))
        return r.json()
    
    def get_barcode_defaults(self):
        """Get the defaults for creating new barcodes."""
        r = requests.get(urljoin(self._base_url, "/barcodes/new.json"))
        return r.json()
    
    def create_barcode(self, barcode):
        """Creates a new barcode."""
        r = requests.post(urljoin(self._base_url, "/barcodes.json"), json=barcode)
        assert r.ok
        return r.json()
    
    def delete_barcode(self, barcode_id):
        """Delete a barcode."""
        r = requests.delete(urljoin(self._base_url, "/barcodes/{}.json").format(barcode_id))
        assert r.ok
    
    def try_connect(self):
        """Tries to connect to the server."""
        try:
            self.users()
            return True
        except Exception as exc:
            log.error("%s: %s", type(exc), exc)
            return False
        
