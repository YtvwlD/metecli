from . import setup, account, audits

import argparse

import logging
log = logging.getLogger(__name__)

def do():
    parser = argparse.ArgumentParser(description="A command line interface to mete.")
    subparsers = parser.add_subparsers(help="commands")
    setup.setup_cmdline(subparsers)
    account.setup_cmdline(subparsers)
    audits.setup_cmdline(subparsers)
    parser.add_argument("--loglevel", type=str, help="{debug, info, *warning*, error, critical}", default="warning")

    args = parser.parse_args()
    numeric_log_level = getattr(logging, args.loglevel.upper(), None)
    if not numeric_log_level:
        print("Invalid log level.")
        return
    logging.basicConfig(level=numeric_log_level)
    
    log.debug("Parsed args: %s", args)
    if(not hasattr(args, "func")):
        print("You must provide a topic. Please see --help.")
        return
    args.func(args)
