from urllib.parse import urlparse
from typing import Tuple
from .connection import Connection
from .config import Config
from .utils import yn
from . import account

import argparse
import logging
log = logging.getLogger(__name__)

def get_url() -> Tuple[str, Connection]:
    while True:
        given = input("Please enter the url for mete: ")
        if not given.endswith("/"):
            given += "/"
        parsed = urlparse(given)
        if parsed.scheme not in ("http", "https"):
            print("Unknown URL scheme '{}'. Please try again.".format(parsed.scheme))
            continue
        if parsed.scheme != "https":
            if yn("The URL you entered doesn't use HTTPS. Do you want to try again?"):
                continue
            log.warning("Using HTTP. The connection won't be secure.")
        conn = Connection(None, base_url=given)
        if not conn.try_connect():
            print("Couldn't connect to the server. Please try again.")
            continue
        return given, conn

def setup_cmdline(global_subparsers: argparse._SubParsersAction) -> None:
    parser = global_subparsers.add_parser("setup", help="setup the connection and select an account")
    parser.set_defaults(func=do)

def do(args: argparse.Namespace, config: Config) -> None:
    log.info("Starting setup.")
    url, conn = get_url()
    config["connection"]["base_url"] = url
    api_version = conn.determine_api_version()
    config["connection"]["api_version"] = api_version
    config.save()
    log.info("URL '%s' (API version %s) configured.", url, api_version)
    if yn("Do want to setup an account now?"):
        if not yn("Do you already have an account?"):
            account.create(args, config)
        account.select(args, config)
    log.info("Setup finished.")
