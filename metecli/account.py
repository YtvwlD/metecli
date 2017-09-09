from .connection import Connection
from . import audits
from .utils import fuzzy_search, true_false_to_yes_no, show_edit

import logging
log = logging.getLogger(__name__)

from tabulate import tabulate

def setup_cmdline(global_subparsers):
    parser = global_subparsers.add_parser("account", help="show or modify an account")
    subparsers = parser.add_subparsers(help="action")
    parser_show = subparsers.add_parser("show", help="display some information")
    parser_show.set_defaults(func=lambda args, config: Account(config).show(args))
    parser_modify = subparsers.add_parser("modify", help="modify your settings")
    parser_modify.set_defaults(func=lambda args, config: Account(config).modify(args))
    parser_buy = subparsers.add_parser("buy", help="buys a drink")
    parser_buy.add_argument("drink", type=str, help="the drink to buy")
    parser_buy.set_defaults(func=lambda args, config: Account(config).buy(args))
    parser_buy_barcode = subparsers.add_parser("buy_barcode", help="buys a drink by barcode")
    parser_buy_barcode.add_argument("barcode", type=int, help="the barcode")
    parser_buy_barcode.set_defaults(func=lambda args, config: Account(config).buy_barcode(args))
    parser_pay = subparsers.add_parser("pay", help="subtracts an amount from your balance")
    parser_pay.add_argument("amount", type=float, help="the amount to subtract")
    parser_pay.set_defaults(func=lambda args, config: Account(config).pay(args))
    parser_deposit = subparsers.add_parser("deposit", help="add an amount to your balance")
    parser_deposit.add_argument("amount", type=float, help="the amount to add")
    parser_deposit.set_defaults(func=lambda args, config: Account(config).deposit(args))
    parser_logs = subparsers.add_parser("logs", help="display the logs")
    parser_logs.set_defaults(func=lambda args, config: Account(config).logs(args))
    parser.set_defaults(func=lambda args, config: Account(config).show(args))

class Account():
    def __init__(self, config):
        self._conf = config
        if "base_url" not in self._conf.settings["connection"]:
            raise Exception("Connection is not configured yet. Account management isn't possible.")
        else:
            self._conn = Connection(base_url=config.settings["connection"]["base_url"])
        if "uid" not in self._conf.settings["connection"]:
            raise Exception("User account is not configured yet. Account management isn't possible.")
        else:
            self._uid = self._conf.settings["connection"]["uid"]
    
    def show(self, args):
        """Displays information about this user."""
        data = self._conn.get_user(self._uid)
        table_data = [
            ["ID", data["id"]],
            ["name", data["name"]],
            ["email", data["email"]],
            ["account balance", "{:.2f} €".format(float(data["balance"]))],
            ["active?", true_false_to_yes_no(data["active"])],
            ["log transactions?", true_false_to_yes_no(data["audit"])],
            ["redirect after buying something?", true_false_to_yes_no(data["redirect"])]
        ]
        print(tabulate(
            table_data,
            tablefmt=self._conf.settings["display"]["table_format"]
        ))
        
    def modify(self, args):
        """Modify settings."""
        data = self._conn.get_user(self._uid)
        log.debug("Editing account. Old data: %s", data)
        show_edit(data, "name", "name", str)
        show_edit(data, "email", "email", "email")
        show_edit(data, "balance", "account balance", float)
        data["balance"] = str(data["balance"])
        show_edit(data, "active", "active?", bool)
        show_edit(data, "audit", "log transactions?", bool)
        show_edit(data, "redirect", "redirect after buying something?", bool)
        log.debug("Editing account. New data: %s", data)
        self._conn.modify_user(data)
    
    def logs(self, args):
        """The same as `audits --user <this user>`."""
        audits.show(self._conf, user=str(self._uid))
    
    def buy(self, args):
        drink_found = fuzzy_search(self._conn, "drink", args.drink)
        if drink_found:
            self._conn.buy(self._uid, drink_found["id"])
    
    def buy_barcode(self, args):
        pass
    
    def pay(self, args):
        log.info("Paying %f...", args.amount)
        self._conn.pay(self._uid, args.amount)
    
    def deposit(self, args):
        log.info("Depositing %f...", args.amount)
        self._conn.deposit(self._uid, args.amount)
