from urllib.parse import urlparse
from .connection import Connection
from .utils import yn
from . import account

import logging
log = logging.getLogger(__name__)

def get_url():
    while True:
        given = input("Please enter the url for mete: ")
        parsed = urlparse(given)
        if parsed.scheme not in ("http", "https"):
            print("Unknown URL scheme '{}'. Please try again.".format(parsed.scheme))
            continue
        if parsed.scheme != "https":
            if yn("The URL you entered doesn't use HTTPS. Do you want to try again?"):
                continue
            log.warning("Using HTTP. The connection won't be secure.")
        if not Connection(base_url=given).try_connect():
            print("Couln't connect to the server. Please try again.")
            continue
        return given

def setup_cmdline(global_subparsers):
    parser = global_subparsers.add_parser("setup", help="setup the connection and select an account")
    parser.set_defaults(func=do)

def do(args, config):
    log.info("Starting setup.")
    url = get_url()
    config["connection"]["base_url"] = url
    config.save()
    log.info("URL '%s' configured.", url)
    if yn("Do want to setup an account now?"):
        if not yn("Do you already have an account?"):
            account.create(args, config)
        account.select(args, config)
    log.info("Setup finished.")
