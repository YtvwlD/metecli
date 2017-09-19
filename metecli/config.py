import yaml
import os
import sys
from contextlib import suppress

import logging
log = logging.getLogger(__name__)

DEFAULT_SETTINGS = {
    "version": 2,
    "connection": {},
    "display": {
        "table_format": "grid",
        "log_level": "warning",
    }
}

def setup_cmdline(global_subparsers):
    parser = global_subparsers.add_parser("config", help="modify the configuration")
    subparsers = parser.add_subparsers(help="action")
    parser_display = subparsers.add_parser("display", help="displays the current config")
    parser_display.set_defaults(func=display)
    parser_get = subparsers.add_parser("get", help="retrieves a specific value")
    parser_get.add_argument("key", help="the key to search for")
    parser_get.set_defaults(func=get)
    parser_set = subparsers.add_parser("set", help="sets a specific value")
    parser_set.add_argument("key", help="the key to set")
    parser_set.add_argument("value", help="the value to set")
    parser_set.set_defaults(func=set)
    parser.set_defaults(func=display)

def display(args, config):
    print(yaml.safe_dump(config._settings, default_flow_style=False))

def handle_KeyError(func):
    def new_func(args, config):
        try:
            return func(args, config)
        except KeyError:
            print("This configuration key doesn't exist.")
    return new_func

@handle_KeyError
def get(args, config):
    path = args.key.split(".")
    current = config
    for part in path:
        if part:
            current = current[part]
    print(current)

@handle_KeyError
def set(args, config):
    path = args.key.split(".")
    current = config._settings
    for i in range(len(path)):
        with suppress(IndexError):
            if path[i] and path[i+1]:
                current = current[path[i]]
    if isinstance(current[path[-1]], dict):
        print("The key you selected is no leaf. It can't be set to a value.")
        return
    current[path[-1]] = args.value
    log.info("Set %s to '%s'.", args.key, args.value)
    config.save()

class Config():
    def __init__(self, path=None, name=None):
        self._search_config_file_path(path, name)
        self._open_or_create()
        self._migrate()
    
    def __getitem__(self, key):
        return self._settings[key]
    
    def __setitem__(self, key, value):
        self._settings[key] = value
    
    def __delitem__(self, key):
        del self._settings[key]
    
    def __contains__(self, key):
        return key in self._settings
    
    def __repr__(self):
        return repr(self._settings)
    
    def _search_config_file_path(self, path, name):
        if path:
            log.info("Config path was specified: %s", path)
            config_path = path
        else:
            config_base_path = None
            try:
                from xdg.BaseDirectory import xdg_config_home
                config_base_path = xdg_config_home
            except ImportError:
                log.info("Couldn't load xdg. Falling back to XDG_CONFIG_HOME.")
                if "XDG_CONFIG_HOME" in os.environ:
                    config_base_path = os.environ["XDG_CONFIG_HOME"]
                else:
                    log.info("Couldn't find XDG_CONFIG_HOME in enviroment. Falling back to platform-specific defaults.")
                    if sys.platform == "linux":
                        config_base_path = os.path.join(os.environ["HOME"], ".config")
                    elif sys.platform == "darwin":
                        config_base_path = os.path.join(os.environ["HOME"], "Library/Application Support")
                    elif sys.platform == "windows":
                        assert os.environ.get("APPDATA")
                        config_base_path = os.environ["APPDATA"]
                    else:
                        log.error("Unknown platform '%s'. Don't know where to store config.", sys.platform)
                        sys.exit(-1)
            log.debug("Found config base path: %s", config_base_path)
            if not os.path.exists(config_base_path):
                log.error("Config base path '%s' doesn't exist.", config_base_path)
                sys.exit(-1)
            if not os.path.isdir(config_base_path):
                log.error("Config base path '%s' exists but is not a directory.")
                sys.exit(-1)
            config_path = os.path.join(config_base_path, "metecli")
        if not os.path.exists(config_path):
            log.info("Configuration path '%s' doesn't exist. Creating.", config_path)
            os.mkdir(config_path)
        if not os.path.isdir(config_path):
            log.error("Configuration path '%s' exists, but is not a directory.")
            sys.exit(-1)
        if not name:
            name = "config"
        config_file_path = os.path.join(config_path, "{}.yaml".format(name))
        log.debug("Using config file at: %s", config_file_path)
        self.config_file_path = config_file_path
    
    def _open_or_create(self):
        if(os.path.exists(self.config_file_path)):
            log.debug("Config file does already exist. Opening.")
            with open(self.config_file_path, "rt") as config_file:
                self._settings = yaml.safe_load(config_file)
        else:
            log.debug("Config file doesn't exist yet. Creating.")
            with open(self.config_file_path, "wt") as config_file:
                pass
            self._settings = dict(DEFAULT_SETTINGS)
            self.save()
    
    def _migrate(self):
        if "version" not in self: # v0 -> v1
            log.info("Configuration doesn't have a version. Asssuming v1.")
            self["version"] = 1
            self.save()
        if self["version"] == 1: # v1 -> v2
            log.info("Migrating to v2: Adding display.log_level.")
            self["display"]["log_level"] = "warning"
            self["version"] = 2
            self.save()
    
    def save(self):
        log.debug("Saving config....")
        with open(self.config_file_path, "wt") as config_file:
            yaml.safe_dump(self._settings, stream=config_file, default_flow_style=False)
