from . import setup, account

import argparse

import logging
log = logging.getLogger(__name__)

def do():
    parser = argparse.ArgumentParser(description="A command line interface to mete.")
    subparsers = parser.add_subparsers(help="commands")
    setup.setup_cmdline(subparsers)
    account.setup_cmdline(subparsers)

    args = parser.parse_args()
    log.debug("commandline: Parsed args: {}".format(args))
    if(not hasattr(args, "func")):
        log.warning("commandline: No topic provided.")
        print("You must provide a topic.")
        print("Please see '--help'.")
        return
    args.func(args)
