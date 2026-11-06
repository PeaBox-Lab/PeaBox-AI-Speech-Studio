from dataclasses import dataclass
from typing import Any, Callable

@dataclass
class AppContext:
    version: str
    store: Any
    project: Any
    preferences: dict
    configured_providers: Callable[[], set[str]]
    open_project: Callable[[str], None]
    save_project: Callable[[Any], None]
    set_active_project: Callable[[Any], None]
