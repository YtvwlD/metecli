import yaml
import os
import sys

import logging
log = logging.getLogger(__name__)

DEFAULT_SETTINGS = {
    "connection": {},
    "display": {
        "table_format": "grid",
    }
}

class Config():
    def __init__(self):
        self._search_config_file_path()
        self._open_or_create()
    
    def _search_config_file_path(self):
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
        config_path = os.path.join(config_base_path, "metecli")
        if not os.path.exists(config_path):
            log.info("Configuration path '%s' doesn't exist. Creating.", config_path)
            os.mkdir(config_path)
        if not os.path.isdir(config_path):
            log.error("Configuration path '%s' exists, but is not a directory.")
            sys.exit(-1)
        config_file_path = os.path.join(config_path, "config.yaml")
        log.debug("Using config file at: %s", config_file_path)
        self.config_file_path = config_file_path
    
    def _open_or_create(self):
        if(os.path.exists(self.config_file_path)):
            log.debug("Config file does already exist. Opening.")
            with open(self.config_file_path, "rt") as config_file:
                self.settings = yaml.load(config_file)
        else:
            log.debug("Config file doesn't exist yet. Creating.")
            with open(self.config_file_path, "wt") as config_file:
                pass
            self.settings = dict(DEFAULT_SETTINGS)
            self.save()
    
    def save(self):
        log.debug("Saving config....")
        with open(self.config_file_path, "wt") as config_file:
            yaml.dump(self.settings, stream=config_file)
