from typing import Any, Dict, Callable

DEFAULT_SETTINGS = {
    "base_url": None,
    "api_version": None,
}


class Config:
    def __init__(
        self, config: Dict[str, Any], save_func: Callable[[], None]
    ) -> None:
        self._settings = config
        self._save_func = save_func
    
    def __getitem__(self, key: str) -> Any:
        return self._settings[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        self._settings[key] = value
    
    def __repr__(self) -> str:
        return repr(self._settings)
    
    def save(self) -> None:
        self._save_func()
