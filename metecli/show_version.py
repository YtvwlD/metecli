from . import _version
from .config import Config

import argparse
import sys
import logging
log = logging.getLogger(__name__)

def setup_cmdline(global_subparsers: argparse._SubParsersAction) -> None:
    parser = global_subparsers.add_parser("version", help="display the version of metecli")
    parser.set_defaults(func=do)

def do(args: argparse.Namespace, config: Config) -> None:
    print("This is metecli v{} running on Python {}.".format(_version, "".join(sys.version.splitlines())))
    log.info("Looking for the version of your config? Run: metecli config get version")
