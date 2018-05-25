from . import setup, account, audits, drinks, config, show_version
from .utils import test_terminal_utf8

import argparse

import logging
log = logging.getLogger(__name__)

def setup_logging(log_level: str) -> None:
    numeric_log_level = getattr(logging, log_level.upper(), None) # type: int
    if not numeric_log_level:
        raise Exception("Invalid log level: {}".format(log_level))
    logging.basicConfig(level=numeric_log_level)

def do() -> None:
    parser = argparse.ArgumentParser(description="A command line interface to mete.")
    subparsers = parser.add_subparsers(help="commands")
    setup.setup_cmdline(subparsers)
    account.setup_cmdline(subparsers)
    audits.setup_cmdline(subparsers)
    drinks.setup_cmdline(subparsers)
    config.setup_cmdline(subparsers)
    show_version.setup_cmdline(subparsers)
    parser.add_argument("--log_level", type=str, help="{debug, info, warning, error, critical}")
    parser.add_argument("--config_path", type=str, help="the path where to place the config file(s)")
    parser.add_argument("--config_name", type=str, help="the name of the config to use")

    args = parser.parse_args() # type: argparse.Namespace
    if args.log_level:
        setup_logging(args.log_level)
    
    log.debug("Parsed args: %s", args)
    if(not hasattr(args, "func")):
        print("You must provide a topic. Please see --help.")
        return
    
    conf = config.Config(path=args.config_path, name=args.config_name)
    
    if not args.log_level:
        setup_logging(conf["display"]["log_level"])
    
    test_terminal_utf8()
    args.func(args, conf)
