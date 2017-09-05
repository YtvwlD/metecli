from .config import Config
from .connection import Connection
from .utils import fuzzy_search

from contextlib import suppress
from tabulate import tabulate

def setup_cmdline(global_subparsers):
    parser = global_subparsers.add_parser("audits", help="show audits")
    parser.add_argument("--user", type=str, help="show only audits for the user USER")
    parser.set_defaults(func=do)

def do(args):
    show(args.user)

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
    if user:
        user_found = fuzzy_search(conn, "user", user)
        if user_found:
            audits = conn.audits(user=user_found["id"])
        else:
            return
    else:
        audits = conn.audits()
    drinks = conn.drinks()
    print("Audits", end="")
    if user:
        print(" for user {}".format(user), end="")
    print(":")
    print(tabulate(_create_table(audits, drinks), headers=["time", "drink", "difference"], tablefmt=config.settings["display"]["table_format"]))
