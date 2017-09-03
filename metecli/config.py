import yaml
import os
import sys

DEFAULT_SETTINGS = {
    "connection": {},
}

class Config():
    def __init__(self, log=None):
        self._log = log
        self._search_config_file_path()
        self._open_or_create()
    
    def _search_config_file_path(self):
        config_base_path = None
        try:
            from xdg.BaseDirectory import xdg_config_home
            config_base_path = xdg_config_home
        except ImportError:
            self._log.info("Couldn't load xdg. Falling back to XDG_CONFIG_HOME.")
            if "XDG_CONFIG_HOME" in os.environ:
                config_base_path = os.environ["XDG_CONFIG_HOME"]
            else:
                self._log.info("Couldn't find XDG_CONFIG_HOME in enviroment. Falling back to platform-specific defaults.")
                if sys.platform == "linux":
                    config_base_path = os.path.join(os.environ["HOME"], ".config")
                else:
                    self._log.error("Unknown platform {}. Don't know where to store config.".format(sys.platform))
                    sys.exit(-1)
        self._log.debug("Found config base path: {}".format(config_base_path))
        config_file_path = os.path.join(config_base_path, "metecli.yaml")
        self._log.debug("Using config file at: {}".format(config_file_path))
        self.config_file_path = config_file_path
    
    def _open_or_create(self):
        if(os.path.exists(self.config_file_path)):
            self._log.debug("Config file does already exist. Opening.")
            with open(self.config_file_path, "rt") as config_file:
                self.settings = yaml.load(config_file)
        else:
            self._log.debug("Config file doesn't exist yet. Creating.")
            with open(self.config_file_path, "wt") as config_file:
                pass
            self.settings = dict(DEFAULT_SETTINGS)
    
    def save(self):
        self._log.debug("Saving config....")
        with open(self.config_file_path, "wt") as config_file:
            yaml.dump(self.settings, stream=config_file)
