from . import setup, account, audits
from .config import Config
from .utils import test_terminal_utf8

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
    parser.add_argument("--configpath", type=str, help="the path where to place the config file(s)")
    parser.add_argument("--configname", type=str, help="the name of the config to use")

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
    
    config = Config(path=args.configpath, name=args.configname)
    test_terminal_utf8()
    args.func(args, config)
