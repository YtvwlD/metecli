from .config import Config
from .connection.connection import Connection
from .connection.models import Drink, User
from . import audits
from .utils import (
    fuzzy_search, true_false_to_yes_no, show_edit, find_by_id, print_table, yn,
    connect, EMail,
)

from typing import List, Optional
import argparse
import logging
log = logging.getLogger(__name__)


def setup_cmdline(global_subparsers: argparse._SubParsersAction) -> None:
    parser = global_subparsers.add_parser(
        "account", help="show or modify an account",
    )
    subparsers = parser.add_subparsers(help="action")
    parser_create = subparsers.add_parser(
        "create", help="creates a new account",
    )
    parser_create.set_defaults(func=create)
    parser_select = subparsers.add_parser(
        "select", help="select the account to use",
    )
    parser_select.set_defaults(func=select)
    parser_show = subparsers.add_parser(
        "show", help="display some information",
    )
    parser_show.set_defaults(
        func=lambda args, config: Account(config).show(args),
    )
    parser_modify = subparsers.add_parser(
        "modify", help="modify your settings",
    )
    parser_modify.set_defaults(
        func=lambda args, config: Account(config).modify(args),
    )
    parser_delete = subparsers.add_parser(
        "delete", help="deletes your account",
    )
    parser_delete.add_argument(
        "--force", action="store_true", help="don't confirm the deletion",
    )
    parser_delete.set_defaults(
        func=lambda args, config: Account(config).delete(args),
    )
    parser_buy = subparsers.add_parser("buy", help="buys a drink")
    parser_buy.add_argument("drink", type=str, help="the drink to buy")
    parser_buy.set_defaults(func=lambda args, config: Account(config).buy(args))
    parser_buy_barcode = subparsers.add_parser(
        "buy_barcode", help="buys a drink by barcode",
    )
    parser_buy_barcode.add_argument("barcode", type=str, help="the barcode")
    parser_buy_barcode.set_defaults(
        func=lambda args, config: Account(config).buy_barcode(args),
    )
    parser_pay = subparsers.add_parser(
        "pay", help="subtracts an amount from your balance",
    )
    parser_pay.add_argument(
        "amount", type=float, help="the amount to subtract",
    )
    parser_pay.set_defaults(
        func=lambda args, config: Account(config).pay(args),
    )
    parser_deposit = subparsers.add_parser(
        "deposit", help="add an amount to your balance",
    )
    parser_deposit.add_argument("amount", type=float, help="the amount to add")
    parser_deposit.set_defaults(
        func=lambda args, config: Account(config).deposit(args),
    )
    parser_transfer = subparsers.add_parser(
        "transfer", help="transfer an amount to a different account",
    )
    parser_transfer.add_argument(
        "receiver", type=str, help="the receiving user",
    )
    parser_transfer.add_argument(
        "amount", type=float, help="the amount to transfer",
    )
    parser_transfer.set_defaults(
        func=lambda args, config: Account(config).transfer(args),
    )
    parser_logs = subparsers.add_parser("logs", help="display the logs")
    parser_logs.set_defaults(
        func=lambda args, config: Account(config).logs(args),
    )
    parser.set_defaults(func=lambda args, config: Account(config).show(args))


def edit_user(data: User) -> None:
    show_edit(data, "name", "name", str)
    show_edit(data, "email", "email", EMail)
    show_edit(data, "balance", "account balance", float)
    show_edit(data, "active", "active?", bool)
    show_edit(data, "audit", "log transactions?", bool)
    show_edit(data, "redirect", "redirect after buying something?", bool)


def create(args: argparse.Namespace, config: Config) -> None:
    conn = connect(config)
    user = conn.get_user_defaults()
    log.debug("Creating new user. Default data: %s", user)
    edit_user(user)
    log.debug("Creating new user. Data: %s", user)
    user = conn.add_user(user)
    log.info("Created new user. Data: %s", user)


def get_uid(conn: Connection) -> int:
    log.info("Loading all users...")
    users = conn.users()
    while True:
        found = False
        given = input(
            "Please enter your username (or a part of it) or your uid: "
        )
        if given.isdecimal():
            uid = int(given)
            if find_by_id(users, uid):
                found = True
        else:
            for user in users:
                if given.casefold() in user.name.casefold():
                    if yn("Is '{}' ({}) your account?".format(
                        user.name, user.email,
                    )):
                        uid = user.id
                        found = True
                        break
        if found:
            return uid
        else:
            print("No matching account found. Please try again.")


def select(args: argparse.Namespace, config: Config) -> None:
    conn = connect(config)
    uid = get_uid(conn)
    config["account"]["uid"] = uid
    config.save()
    log.info("UID %i configured.", uid)


class Account():
    def __init__(self, config: Config) -> None:
        self._conf = config
        self._conn = connect(config)
        if not self._conf["account"]["uid"]:
            raise Exception("User account is not configured yet. Account management isn't possible.")
        else:
            self._uid = self._conf["account"]["uid"]
    
    def show(self, args: argparse.Namespace) -> None:
        """Displays information about this user."""
        data = self._conn.get_user(self._uid)
        self._print_user(data)
    
    def _print_user(self, user: User) -> None:
        table_data = (
            ("ID", user.id),
            ("name", user.name),
            ("email", user.email),
            ("account balance", "{:.2f} €".format(user.balance)),
            ("active?", true_false_to_yes_no(user.active)),
            ("log transactions?", true_false_to_yes_no(user.audit)),
            (
                "redirect after buying something?",
                true_false_to_yes_no(user.redirect)
            ),
        )
        print_table(self._conf, table_data)
        
    def modify(self, args: argparse.Namespace) -> None:
        """Modify settings."""
        data = self._conn.get_user(self._uid)
        log.debug("Editing account. Old data: %s", data)
        edit_user(data)
        log.info("Editing account. New data: %s", data)
        self._conn.modify_user(data)
    
    def logs(self, args: argparse.Namespace) -> None:
        """The same as `audits --user <this user>`."""
        audits.show(self._conf, self._conn, user=str(self._uid))
    
    def buy(self, args: argparse.Namespace) -> None:
        drink_found = fuzzy_search(self._conn.drinks(), args.drink)
        if drink_found:
            self._buy(drink_found)
    
    def buy_barcode(self, args: argparse.Namespace) -> None:
        barcodes = self._conn.barcodes()
        drinks = self._conn.drinks()
        barcode = find_by_id(barcodes, args.barcode)
        if not barcode:
            print("Couldn't find a drink with this barcode.")
            return
        drink = find_by_id(drinks, barcode.drink)
        if not drink:
            print("Couldn't find a drink with this barcode.")
            return
        self._buy(drink)
    
    def _buy(self, drink: Drink) -> None:
        log.info("Buying %s...", drink.name)
        self._conn.buy(self._uid, drink.id)
        data = self._conn.get_user(self._uid)
        log.info("Success! You bought {} and your new balance is {}.".format(
            drink.name, data.balance
        ))
        if data.balance < 0:
            log.warn("Your balance is below zero. Remember to compensate as soon as possible.")
        if data.audit:
            log.info("This transaction has been logged, because you set up your account that way.")
    
    def pay(self, args: argparse.Namespace) -> None:
        log.info("Paying %f...", args.amount)
        self._conn.pay(self._uid, args.amount)
    
    def deposit(self, args: argparse.Namespace) -> None:
        log.info("Depositing %f...", args.amount)
        self._conn.deposit(self._uid, args.amount)
    
    def transfer(self, args: argparse.Namespace) -> None:
        receiver_found = fuzzy_search(self._conn.users(), args.receiver)
        if not receiver_found:
            print("Couldn't find a receiver with this name.")
            return
        log.info("Transferring %f to %s...", args.amount, receiver_found.name)
        self._conn.transfer(self._uid, receiver_found.id, args.amount)
    
    def delete(self, args: argparse.Namespace) -> None:
        user = self._conn.get_user(self._uid)
        if not args.force:
            log.debug("About to delete account '%s'.", user.name)
            print(
                "You are about to delete the account '{}'.".format(user.name)
            )
            if not yn("Are you sure about this?"):
                log.debug("Deletion cancelled.")
                return
            given = input("Then please enter the name of the account you want to delete: ")
            if given != user.name:
                log.debug("Deletion cancelled.")
                print("This was not correct. Cancelling deletion.")
                return
            given = input("Then please enter the email address of the account you want to delete: ")
            if given != user.email:
                log.debug("Deletion cancelled.")
                print("This was not correct. Cancelling deletion.")
                return
            print("You are about to delete this account:")
            self._print_user(user)
            print("This cannot be undone.")
            if not yn("Are you really sure about this?"):
                log.debug("Deletion cancelled.")
                return
        self._conn.delete_user(user.id)
        self._conf["account"]["uid"] = None
        self._conf.save()
        self._uid = None
        log.info("Deleted account '%s'.", user.name)
