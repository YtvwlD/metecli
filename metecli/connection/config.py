from typing import Dict, Callable

DEFAULT_SETTINGS =  {
    "base_url": None,
    "api_version": None,
}

class Config:
    def __init__(self, config: Dict[str, object], save_func: Callable[[], None]) -> None:
        self._settings = config
        self._save_func = save_func
    
    def __getitem__(self, key: str) -> object:
        return self._settings[key]
    
    def __setitem__(self, key: str, value: object) -> None:
        self._settings[key] = value
    
    def __repr__(self) -> str:
        return repr(self._settings)
    
    def save(self) -> None:
        self._save_func()
