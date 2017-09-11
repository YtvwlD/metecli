from .utils import fuzzy_search, find_by_id, print_table, with_connection

from datetime import datetime
from argparse import ArgumentTypeError

import logging
log = logging.getLogger(__name__)

def valid_date(value): # taken from https://stackoverflow.com/a/25470943/2192464
    try:
        return datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{}'.".format(value)
        raise ArgumentTypeError(msg)

def setup_cmdline(global_subparsers):
    parser = global_subparsers.add_parser("audits", help="show audits")
    parser.add_argument("--user", type=str, help="show only audits for the user USER")
    parser.add_argument("--from_date", type=valid_date, help="show only audits that were created after this date")
    parser.add_argument("--to_date", type=valid_date, help="show only audits that were created before this date")
    parser.set_defaults(func=do)

@with_connection
def do(args, config, conn):
    show(config, conn, user=args.user, from_date=args.from_date, to_date=args.to_date)

def _create_table(audits, drinks):
    for audit in audits["audits"]:
        drink = None
        if audit["drink"]:
            drink = find_by_id(drinks, audit["drink"])
        if not drink:
            drink = {"name": "n/a"}
        yield [audit["created_at"], drink["name"], audit["difference"]]

def show(config, conn, user=None, from_date=None, to_date=None):
    params = dict()
    if user:
        user_found = fuzzy_search(conn.users(), user)
        if user_found:
            params["user"] = user_found["id"]
        else:
            return
    if from_date:
        params["from_date"] = from_date
    if to_date:
        params["to_date"] = to_date
    if (from_date or to_date) and not (from_date and to_date):
        log.warn("Either from_date or to_date was given but not the other one. This might fail.")
    audits = conn.audits(**params)
    drinks = conn.drinks()
    print("Audits", end="")
    if user:
        print(" for user {}".format(user), end="")
    print(":")
    print_table(config, _create_table(audits, drinks), headers=["time", "drink", "difference"])
