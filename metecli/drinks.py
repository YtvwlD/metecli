from .utils import true_false_to_yes_no, fuzzy_search, print_table, show_edit, with_connection, yn

import logging
log = logging.getLogger(__name__)

def setup_cmdline(global_subparsers):
    parser = global_subparsers.add_parser("drinks", help="show or modify drinks")
    subparsers = parser.add_subparsers(help="action")
    parser_list = subparsers.add_parser("list", help="lists all drinks")
    parser_list.set_defaults(func=list_drinks)
    parser_add = subparsers.add_parser("add", help="creates a new drink")
    parser_add.set_defaults(func=add_drink)
    parser_show = subparsers.add_parser("show", help="display detailed information about a drink")
    parser_show.add_argument("drink", help="the drink to display")
    parser_show.set_defaults(func=show)
    parser_modify = subparsers.add_parser("modify", help="edits a drink")
    parser_modify.add_argument("drink", help="the drink to modify")
    parser_modify.set_defaults(func=modify)
    parser_barcodes = subparsers.add_parser("barcodes", help="manage barcodes for this drink")
    parser_barcodes.add_argument("drink", help="the drink")
    parser_barcodes.set_defaults(func=barcodes_list)
    subparsers_barcodes = parser_barcodes.add_subparsers(help="action")
    parser_barcodes_list = subparsers_barcodes.add_parser("list", help="list all barcodes for this drink")
    parser_barcodes_list.set_defaults(func=barcodes_list)
    parser_barcodes_add = subparsers_barcodes.add_parser("add", help="add a barcode for this drink")
    parser_barcodes_add.add_argument("barcode", help="the barcode to add")
    parser_barcodes_add.set_defaults(func=barcodes_add)
    parser_delete = subparsers.add_parser("delete", help="deletes a drink")
    parser_delete.add_argument("drink", help="the drink to delete")
    parser_delete.add_argument("--force", action="store_true", help="don't confirm the deletion")
    parser_delete.set_defaults(func=delete)
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
    print_drink(drink, config)

def print_drink(drink, config):
    print_table(config, [
            ["ID", drink["id"]],
            ["name", drink["name"]],
            ["price", "{:.2f} €".format(float(drink["price"]))],
            ["bottle size", drink["bottle_size"]],
            ["caffeine", drink["caffeine"]],
            ["active?", true_false_to_yes_no(drink["active"])],
    ])

def edit_drink(data):
    show_edit(data, "name", "name", str)
    show_edit(data, "price", "price", float)
    show_edit(data, "bottle_size", "bottle size", float)
    show_edit(data, "caffeine", "caffeine", int)
    show_edit(data, "active", "active?", bool)

@with_connection
def add_drink(args, config, conn):
    data = conn.get_drink_defaults()
    log.debug("Creating a new drink. Default data: %s", data)
    edit_drink(data)
    log.debug("Creating a new drink. Data: %s", data)
    data = conn.create_drink(data)
    log.info("Created a new drink. Data: %s", data)

@with_connection
def modify(args, config, conn):
    data = fuzzy_search(conn.drinks(), args.drink)
    if not data:
        return
    log.debug("Editing drink. Old data: %s", data)
    edit_drink(data)
    log.info("Editing drink. New data: %s", data)
    conn.modify_drink(data)

@with_connection
def barcodes_list(args, config, conn):
    drink = fuzzy_search(conn.drinks(), args.drink)
    if not drink:
        return
    all_barcodes = conn.barcodes()
    barcodes = list()
    for barcode in all_barcodes:
        if barcode["drink"] == drink["id"]:
            barcodes.append([barcode["id"]])
    print_table(config, barcodes)

@with_connection
def barcodes_add(args, config, conn):
    drink = fuzzy_search(conn.drinks(), args.drink)
    if not drink:
        return
    barcode = conn.get_barcode_defaults()
    barcode["drink"] = drink["id"]
    barcode["id"] = args.barcode
    log.debug("Creating new barcode '%s' for drink '%s'.", barcode["id"], drink["name"])
    barcode = conn.create_barcode(barcode)
    log.info("Created new barcode '%s' for dirnk '%s'.", barcode["id"], drink["name"])

@with_connection
def delete(args, config, conn):
    drink = fuzzy_search(conn.drinks(), args.drink)
    if not drink:
        return
    if not args.force:
        log.debug("About to delete drink %s.", drink["name"])
        print("You are about to delete the drink '{}'.".format(drink["name"]))
        if not yn("Are you sure about this?"):
            log.debug("Deletion cancelled.")
            return
        given = input("Then please enter the name of the drink you want to delete: ")
        if given != drink["name"]:
            log.debug("Deletion cancelled.")
            print("This was not correct. Cancelling deletion.")
            return
        print("You are about to delete this drink:")
        print_drink(drink, config)
        print("This cannot be undone.")
        if not yn("Are you really sure about this?"):
            log.debug("Deletion cancelled.")
            return
    conn.delete_drink(drink["id"])
    log.info("Deleted drink '%s'.", drink["name"])
