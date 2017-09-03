from urllib.parse import urlparse
from .connection import Connection
from .config import Config

import logging
log = logging.getLogger(__name__)

def yn(prompt):
    while True:
        entered = input("{} (y/n) ".format(prompt))
        if entered in ("yes", "y"):
            return True
        if entered in ("no", "n"):
            return False
        print("Please enter 'yes' or 'no'.")

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

def get_uid(url=None):
    conn = Connection(base_url=url)
    users = conn.users()
    while True:
        found = False
        given = input("Please enter your username (or a part of it) or your uid: ")
        for user in users:
            if given.isdecimal():
                uid = int(given)
                if user["id"] == uid:
                    found = True
                    break
            else:
                if given in user["name"]:
                    if yn("Is '{}' ({}) your account?".format(user["name"], user["email"])):
                        uid = user["id"]
                        found = True
                        break
        if found:
            return uid
        else:
            print("No matching account found. Please try again.")

def setup_cmdline(global_subparsers):
    parser = global_subparsers.add_parser("setup", help="setup the connection and select an account")
    parser.set_defaults(func=do)

def do(args):
    config = Config()
    log.debug("Starting setup.")
    url = get_url()
    config.settings["connection"]["base_url"] = url
    config.save()
    log.debug("URL '%s' configured.", url)
    uid = get_uid(url=url)
    config.settings["connection"]["uid"] = uid
    config.save()
    log.debug("UID %i configured.", uid)
