from .config import Config
from .connection import Connection
from . import audits

import logging
log = logging.getLogger(__name__)

def do(args):
    print("Please select an action (see '--help').")

def setup_cmdline(global_subparsers):
    acc = Account()
    parser = global_subparsers.add_parser("account", help="show or modify an account")
    subparsers = parser.add_subparsers(help="action")
    parser_buy = subparsers.add_parser("buy", help="buys a drink")
    parser_buy.add_argument("drink", type=str, help="the drink to buy")
    parser_buy.set_defaults(func=acc.buy)
    parser_buy_barcode = subparsers.add_parser("buy_barcode", help="buys a drink by barcode")
    parser_buy_barcode.add_argument("barcode", type=int, help="the barcode")
    parser_buy_barcode.set_defaults(func=acc.buy_barcode)
    parser_pay = subparsers.add_parser("pay", help="subtracts an amount from your balance")
    parser_pay.add_argument("amount", type=float, help="the amount to subtract")
    parser_pay.set_defaults(func=acc.pay)
    parser_deposit = subparsers.add_parser("deposit", help="add an amount to your balance")
    parser_deposit.add_argument("amount", type=float, help="the amount to add")
    parser_deposit.set_defaults(func=acc.deposit)
    parser_logs = subparsers.add_parser("logs", help="display the logs")
    parser_logs.set_defaults(func=acc.logs)
    parser.set_defaults(func=do)

class Account():
    def __init__(self):
        config = Config()
        if not "base_url" in config.settings["connection"]:
            log.warn("Connection is not configured yet. Account management won't be possible.")
        else:
            self._conn = Connection(base_url=config.settings["connection"]["base_url"])
        if not "uid" in config.settings["connection"]:
            log.warn("User account is not configured yet. Account management won't be possible.")
        else:
            self._uid = config.settings["connection"]["uid"]
    
    def logs(self, args):
        """The same as `audits --user <this user>`."""
        audits.show(user=str(self._uid))
    
    def buy(self, args):
        drinks = self._conn.drinks()
        possible_drinks = list()
        drink_to_buy = None
        for drink in drinks:
            if args.drink.isdecimal():
                if int(args.drink) == drink["id"]:
                    drink_to_buy = drink
                    break
            if args.drink == drink["name"]:
                drink_to_buy = drink
                break
            elif args.drink in drink["name"]:
                possible_drinks.append(drink)
        if not drink_to_buy and len(possible_drinks) == 1:
            log.info("No exact match, but %s is the only possibility.", possible_drinks[0]["name"])
            drink_to_buy = possible_drinks[0]
        if drink_to_buy:
            log.info("Buying drink %s...", drink_to_buy["name"])
            self._conn.buy(self._uid, drink_to_buy["id"])
        elif possible_drinks:
            print("No exactly matching drink was found.")
            print("Possible drinks:", list(map(lambda drink: "{} ({})".format(drink["name"], drink["id"]), possible_drinks)))
        else:
            print("No matching drinks were found.")
    
    def buy_barcode(self, args):
        pass
    
    def pay(self, args):
        log.info("Paying %f...", args.amount)
        self._conn.pay(self._uid, args.amount)
    
    def deposit(self, args):
        log.info("Depositing %f...", args.amount)
        self._conn.deposit(self._uid, args.amount)
