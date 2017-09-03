import argparse

def do(log=None, setup_func=None, account_func=None):
    parser = argparse.ArgumentParser(description="A command line interface to mete.")
    subparsers = parser.add_subparsers(help="commands")
    parser_setup = subparsers.add_parser("setup", help="setup the connection and select an account")
    parser_setup.set_defaults(func=setup_func)
    parser_account = subparsers.add_parser("account", help="show or modify an account")
    # TODO parameters
    parser_account.set_defaults(func=account_func)

    args = parser.parse_args()
    log.debug("commandline: Parsed args: {}".format(args))
    if(not hasattr(args, "func")):
        log.warning("commandline: No topic provided.")
        print("You must provide a topic.")
        print("Please see '--help'.")
        return
    args.func(args, log=log)