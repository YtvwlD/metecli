from .config import Config
from .connection import Connection

from contextlib import suppress
from tabulate import tabulate

def _create_table(audits, drinks):
    for audit in audits["audits"]:
        drink = None
        if audit["drink"]:
            with suppress(IndexError):
                drink = drinks[audit["drink"]]
        if not drink:
            drink = {"name": "n/a"}
        yield [audit["created_at"], drink["name"], audit["difference"]]

def show(user=None):
    config = Config()
    conn = Connection(base_url=config.settings["connection"]["base_url"])
    assert user.isdecimal() # TODO: Support searching for user names.
    audits = conn.audits(user=int(user))
    drinks = conn.drinks()
    print("Audits", end="")
    if user:
        print(" for user {}".format(user), end="")
    print(":")
    print(tabulate(_create_table(audits, drinks), headers=["time", "drink", "difference"], tablefmt=config.settings["display"]["table_format"]))
