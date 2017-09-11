from .connection import Connection
from .utils import true_false_to_yes_no, fuzzy_search

from tabulate import tabulate

def setup_cmdline(global_subparsers):
    parser = global_subparsers.add_parser("drinks", help="show or modify drinks")
    subparsers = parser.add_subparsers(help="action")
    parser_list = subparsers.add_parser("list", help="lists all drinks")
    parser_list.set_defaults(func=list_drinks)
    parser_show = subparsers.add_parser("show", help="display detailed information about a drink")
    parser_show.add_argument("drink", help="the drink to display")
    parser_show.set_defaults(func=show)
    parser.set_defaults(func=list_drinks)

def list_drinks(args, config):
    conn = Connection(base_url=config.settings["connection"]["base_url"])
    drinks = conn.drinks()
    print("All drinks:")
    print(tabulate(
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
        tablefmt=config.settings["display"]["table_format"],
    ))

def show(args, config):
    conn = Connection(base_url=config.settings["connection"]["base_url"])
    drink = fuzzy_search(conn, "drink", args.drink)
    if not drink:
        return
    print(tabulate(
        [
            ["ID", drink["id"]],
            ["name", drink["name"]],
            ["price", "{:.2f} €".format(float(drink["price"]))],
            ["bottle size", drink["bottle_size"]],
            ["caffeine", drink["caffeine"]],
            ["active?", true_false_to_yes_no(drink["active"])],
        ],
        tablefmt=config.settings["display"]["table_format"]
    ))
