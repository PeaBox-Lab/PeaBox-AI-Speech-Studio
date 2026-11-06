from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4
def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
@dataclass
class ScriptBlock:
    title: str
    text: str = ""
    provider: str = "Kokoro local"
    language: str = "US English"
    voice: str = "af_heart"
    speed: float = 1.0
    enabled: bool = True
    id: str = field(default_factory=lambda: uuid4().hex)
    notes: str = ""
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScriptBlock":
        allowed = {key: data[key] for key in cls.__dataclass_fields__ if key in data}
        return cls(**allowed)
@dataclass
class Project:
    name: str
    description: str = ""
    script: str = ""
    id: str = field(default_factory=lambda: uuid4().hex)
    created_at: str = field(default_factory=utc_now)
    updated_at: str = field(default_factory=utc_now)
    settings: dict[str, Any] = field(default_factory=dict)
    render_history: list[dict[str, Any]] = field(default_factory=list)
    blocks: list[ScriptBlock] = field(default_factory=list)
    def touch(self) -> None:
        self.updated_at = utc_now()
    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["blocks"] = [block.to_dict() for block in self.blocks]
        return data
    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Project":
        allowed = {key: data[key] for key in cls.__dataclass_fields__ if key in data and key != "blocks"}
        project = cls(**allowed)
        project.blocks = [ScriptBlock.from_dict(item) for item in data.get("blocks", [])]
        return project