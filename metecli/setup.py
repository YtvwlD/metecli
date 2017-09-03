from urllib.parse import urlparse
from .connection import Connection
from .config import Config

def yn(prompt):
    while True:
        entered = input("{} ".format(prompt))
        if entered in ("yes", "y"):
            return True
        if entered in ("no", "n"):
            return False
        print("Please enter 'yes' or 'no'.")

def get_url(log=None):
    while True:
        given = input("Please enter the url for mete: ")
        parsed = urlparse(given)
        if parsed.scheme not in ("http", "https"):
            print("Unknown URL scheme '{}'. Please try again.".format(parsed.scheme))
            continue
        if parsed.scheme != "https":
            if yn("The URL you entered doesn't use HTTPS. Do you want to try again? (y/n)"):
                continue
            log.warning("Using HTTP. The connection won't be secure.")
        if not Connection(log=log, base_url=given).try_connect():
            print("Couln't connect to the server. Please try again.")
            continue
        return given

def do(args, log=None):
    config = Config(log=log)
    log.debug("Starting setup.")
    url = get_url(log=log)
    config.settings["connection"]["base_url"] = url
    config.save()
    log.debug("Setup: URL '{}' configured.".format(url))
