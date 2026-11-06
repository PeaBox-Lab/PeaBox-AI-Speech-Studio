from dataclasses import dataclass
from typing import Any, Callable

@dataclass
class AppContext:
    version: str
    store: Any
    project: Any
    preferences: dict
    profiles: dict
    voice_catalogs: dict
    configured_providers: Callable[[], set[str]]
    save_project: Callable[[Any], None]
    open_project: Callable[[str], None]
    set_active_project: Callable[[Any], None]
