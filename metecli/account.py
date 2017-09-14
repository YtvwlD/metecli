from .connection import Connection
from . import audits
from .utils import fuzzy_search, true_false_to_yes_no, show_edit, find_by_id, print_table, with_connection, yn

import logging
log = logging.getLogger(__name__)

def setup_cmdline(global_subparsers):
    parser = global_subparsers.add_parser("account", help="show or modify an account")
    subparsers = parser.add_subparsers(help="action")
    parser_create = subparsers.add_parser("create", help="creates a new account")
    parser_create.set_defaults(func=create)
    parser_select = subparsers.add_parser("select", help="select the account to use")
    parser_select.set_defaults(func=select)
    parser_show = subparsers.add_parser("show", help="display some information")
    parser_show.set_defaults(func=lambda args, config: Account(config).show(args))
    parser_modify = subparsers.add_parser("modify", help="modify your settings")
    parser_modify.set_defaults(func=lambda args, config: Account(config).modify(args))
    parser_delete = subparsers.add_parser("delete", help="deletes your account")
    parser_delete.add_argument("--force", action="store_true", help="don't confirm the deletion")
    parser_delete.set_defaults(func=lambda args, config: Account(config).delete(args))
    parser_buy = subparsers.add_parser("buy", help="buys a drink")
    parser_buy.add_argument("drink", type=str, help="the drink to buy")
    parser_buy.set_defaults(func=lambda args, config: Account(config).buy(args))
    parser_buy_barcode = subparsers.add_parser("buy_barcode", help="buys a drink by barcode")
    parser_buy_barcode.add_argument("barcode", type=str, help="the barcode")
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

def edit_user(data):
    show_edit(data, "name", "name", str)
    show_edit(data, "email", "email", "email")
    show_edit(data, "balance", "account balance", float)
    data["balance"] = str(data["balance"])
    show_edit(data, "active", "active?", bool)
    show_edit(data, "audit", "log transactions?", bool)
    show_edit(data, "redirect", "redirect after buying something?", bool)

@with_connection
def create(args, config, conn):
    data = conn.get_user_defaults()
    log.debug("Creating new user. Default data: %s", data)
    edit_user(data)
    log.debug("Creating new user. Data: %s", data)
    data = conn.add_user(data)
    log.info("Created new user. Data: %s", data)

def get_uid(conn):
    log.info("Loading all users...")
    users = conn.users()
    while True:
        found = False
        given = input("Please enter your username (or a part of it) or your uid: ")
        if given.isdecimal():
            uid = int(given)
            if find_by_id(users, uid):
                found = True
        else:
            for user in users:
                if given in user["name"]:
                    if yn("Is '{}' ({}) your account?".format(user["name"], user["email"])):
                        uid = user["id"]
                        found = True
                        break
        if found:
            return uid
        else:
            print("No matching account found. Please try again.")

@with_connection
def select(args, config, conn):
    uid = get_uid(conn)
    config["connection"]["uid"] = uid
    config.save()
    log.info("UID %i configured.", uid)

class Account():
    def __init__(self, config):
        self._conf = config
        if "base_url" not in self._conf["connection"]:
            raise Exception("Connection is not configured yet. Account management isn't possible.")
        else:
            self._conn = Connection(base_url=config["connection"]["base_url"])
        if "uid" not in self._conf["connection"]:
            raise Exception("User account is not configured yet. Account management isn't possible.")
        else:
            self._uid = self._conf["connection"]["uid"]
    
    def show(self, args):
        """Displays information about this user."""
        data = self._conn.get_user(self._uid)
        self._print_user(data)
    
    def _print_user(self, data):
        table_data = [
            ["ID", data["id"]],
            ["name", data["name"]],
            ["email", data["email"]],
            ["account balance", "{:.2f} €".format(float(data["balance"]))],
            ["active?", true_false_to_yes_no(data["active"])],
            ["log transactions?", true_false_to_yes_no(data["audit"])],
            ["redirect after buying something?", true_false_to_yes_no(data["redirect"])]
        ]
        print_table(self._conf, table_data)
        
    def modify(self, args):
        """Modify settings."""
        data = self._conn.get_user(self._uid)
        log.debug("Editing account. Old data: %s", data)
        edit_user(data)
        log.info("Editing account. New data: %s", data)
        self._conn.modify_user(data)
    
    def logs(self, args):
        """The same as `audits --user <this user>`."""
        audits.show(self._conf, self._conn, user=str(self._uid))
    
    def buy(self, args):
        drink_found = fuzzy_search(self._conn.drinks(), args.drink)
        if drink_found:
            log.info("Buying %s...", drink_found["name"])
            self._conn.buy(self._uid, drink_found["id"])
    
    def buy_barcode(self, args):
        barcodes = self._conn.barcodes()
        drinks = self._conn.drinks()
        barcode = find_by_id(barcodes, args.barcode)
        if not barcode:
            print("Couldn't find a drink with this barcode.")
            return
        drink = find_by_id(drinks, barcode["drink"])
        if not drink:
            print("Couldn't find a drink with this barcode.")
            return
        log.info("Buying %s...", drink["name"])
        self._conn.buy(self._uid, drink["id"])
    
    def pay(self, args):
        log.info("Paying %f...", args.amount)
        self._conn.pay(self._uid, args.amount)
    
    def deposit(self, args):
        log.info("Depositing %f...", args.amount)
        self._conn.deposit(self._uid, args.amount)
    
    def delete(self, args):
        user = self._conn.get_user(self._uid)
        if not args.force:
            log.debug("About to delete account '%s'.", user["name"])
            print("You are about to delete the account '{}'.".format(user["name"]))
            if not yn("Are you sure about this?"):
                log.debug("Deletion cancelled.")
                return
            given = input("Then please enter the name of the account you want to delete: ")
            if given != user["name"]:
                log.debug("Deletion cancelled.")
                print("This was not correct. Cancelling deletion.")
                return
            given = input("Then please enter the email address of the account you want to delete: ")
            if given != user["email"]:
                log.debug("Deletion cancelled.")
                print("This was not correct. Cancelling deletion.")
                return
            print("You are about to delete this account:")
            self._print_user(user)
            print("This cannot be undone.")
            if not yn("Are you really sure about this?"):
                log.debug("Deletion cancelled.")
                return
        del self._conf["connection"]["uid"]
        del self._uid
        self._conf.save()
        self._conn.delete_user(user["id"])
        log.info("Deleted account '%s'.", user["name"])
