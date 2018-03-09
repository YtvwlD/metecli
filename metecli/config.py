from .connection import Connection

import yaml
import os
import sys
from contextlib import suppress
from typing import Callable, Optional

import argparse
import logging
log = logging.getLogger(__name__)

DEFAULT_SETTINGS = {
    "version": 4,
    "connection": {
        "base_url": None,
        "api_version": None,
        "uid": None,
    },
    "display": {
        "table_format": "grid",
        "log_level": "warning",
    }
}

def setup_cmdline(global_subparsers: argparse._SubParsersAction) -> None:
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

def display(args: argparse.Namespace, config: 'Config') -> None:
    print(yaml.safe_dump(config._settings, default_flow_style=False))

def handle_KeyError(func: Callable[[argparse.Namespace, 'Config'], None]) -> Callable[[argparse.Namespace, 'Config'], None]:
    def new_func(args: argparse.Namespace, config: 'Config') -> None:
        try:
            func(args, config)
        except KeyError:
            print("This configuration key doesn't exist.")
    return new_func

@handle_KeyError
def get(args: argparse.Namespace, config: 'Config') -> None:
    path = args.key.split(".")
    current = config
    for part in path:
        if part:
            current = current[part]
    print(current)

@handle_KeyError
def set(args: argparse.Namespace, config: 'Config') -> None:
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
    def __init__(self, path: Optional[str] = None, name: Optional[str] = None) -> None:
        self._search_config_file_path(path, name)
        self._open_or_create()
        self._migrate()
    
    def __getitem__(self, key: str):
        return self._settings[key]
    
    def __setitem__(self, key: str, value):
        self._settings[key] = value
    
    def __repr__(self) -> str:
        return repr(self._settings)
    
    def _search_config_file_path(self, path: Optional[str], name: Optional[str]) -> None:
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
    
    def _open_or_create(self) -> None:
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
    
    def _migrate(self) -> None:
        if "version" not in self._settings: # v0 -> v1
            log.info("Configuration doesn't have a version. Asssuming v1.")
            self["version"] = 1
            self.save()
        if self["version"] == 1: # v1 -> v2
            log.info("Migrating to v2: Adding display.log_level.")
            self["display"]["log_level"] = "warning"
            self["version"] = 2
            self.save()
        if self["version"] == 2: # v2 -> v3
            log.info("Migrating to v3: Adding 'uid' and 'base_url' to connection if they don't exist.")
            if "base_url" not in self["connection"]:
                self["connection"]["base_url"] = None
            if "uid" not in self["connection"]:
                self["connection"]["uid"] = None
            self["version"] = 3
            self.save()
        if self["version"] == 3: # v3 -> v4
            log.info("Migrating to v4: Adding connection.api_version.")
            if self["connection"]["base_url"]:
                self["connection"]["api_version"] = Connection(None, base_url=self["connection"]["base_url"]).determine_api_version()
            else:
                self["connection"]["api_version"] = None
            self["version"] = 4
            self.save()
    
    def save(self) -> None:
        log.debug("Saving config....")
        with open(self.config_file_path, "wt") as config_file:
            yaml.safe_dump(self._settings, stream=config_file, default_flow_style=False)
