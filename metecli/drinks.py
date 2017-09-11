from .utils import true_false_to_yes_no, fuzzy_search, print_table, show_edit, with_connection

import logging
log = logging.getLogger(__name__)

def setup_cmdline(global_subparsers):
    parser = global_subparsers.add_parser("drinks", help="show or modify drinks")
    subparsers = parser.add_subparsers(help="action")
    parser_list = subparsers.add_parser("list", help="lists all drinks")
    parser_list.set_defaults(func=list_drinks)
    parser_show = subparsers.add_parser("show", help="display detailed information about a drink")
    parser_show.add_argument("drink", help="the drink to display")
    parser_show.set_defaults(func=show)
    parser_modify = subparsers.add_parser("modify", help="edits a drink")
    parser_modify.add_argument("drink", help="the drink to modify")
    parser_modify.set_defaults(func=modify)
    parser.set_defaults(func=list_drinks)

@with_connection
def list_drinks(args, config, conn):
    drinks = conn.drinks()
    print("All drinks:")
    print_table(config,
        sorted([[
            drink["id"],
            drink["name"],
            drink["bottle_size"],
            drink["caffeine"],
            "{:.2f} €".format(float(drink["price"])),
            true_false_to_yes_no(drink["active"]),
        ] for drink in drinks], key=lambda entry: entry[0]),
        headers=[
            "ID",
            "name",
            "bottle size",
            "caffeine",
            "price",
            "active?"
        ],
    )

@with_connection
def show(args, config, conn):
    drink = fuzzy_search(conn.drinks(), args.drink)
    if not drink:
        return
    print_table(config, [
            ["ID", drink["id"]],
            ["name", drink["name"]],
            ["price", "{:.2f} €".format(float(drink["price"]))],
            ["bottle size", drink["bottle_size"]],
            ["caffeine", drink["caffeine"]],
            ["active?", true_false_to_yes_no(drink["active"])],
    ])

@with_connection
def modify(args, config, conn):
    data = fuzzy_search(conn.drinks(), args.drink)
    if not data:
        return
    log.debug("Editing drink. Old data: %s", data)
    show_edit(data, "name", "name", str)
    show_edit(data, "price", "price", float)
    show_edit(data, "bottle_size", "bottle size", float)
    show_edit(data, "caffeine", "caffeine", int)
    show_edit(data, "active", "active?", bool)
    log.info("Editing drink. New data: %s", data)
    conn.modify_drink(data)
