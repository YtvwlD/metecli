from .config import Config
from .connection import Connection

def do(args):
    print("Please select an action (see '--help').")

def setup_cmdline(global_subparsers, log=None):
    acc = Account(log=log)
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
    parser.set_defaults(func=do)

class Account():
    def __init__(self, log=None):
        self._log = log
        config = Config(log=log)
        self._conn = Connection(log=log, base_url=config.settings["connection"]["base_url"])
        self._uid = config.settings["connection"]["uid"]

    def do(self, args):
        log.info("TODO: account")
    
    def buy(self, args):
        pass
    
    def buy_barcode(self, args):
        pass
    
    def pay(self, args):
        pass
    
    def deposit(self, args):
        pass
