"""Player configuration loading and validation."""
import json
from pathlib import Path

from pydantic import BaseModel, field_validator


class PlayerConfig(BaseModel):
    name: str
    model: str
    backend: str = "ollama"
    personality: str

    @field_validator("name", "model", "personality")
    @classmethod
    def must_not_be_empty(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Field must not be empty or whitespace")
        return value

    @field_validator("backend")
    @classmethod
    def backend_must_be_valid(cls, value: str) -> str:
        allowed = {"ollama", "nvidia", "openai"}
        if value not in allowed:
            raise ValueError(f"backend must be one of {allowed}, got {value!r}")
        return value


def load_player_configs(path: Path) -> list[PlayerConfig]:
    """Load and validate players.json.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If JSON is invalid or any player config fails validation.
    """
    resolved = Path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"Players file not found: {path}")

    try:
        raw = json.loads(resolved.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in players file {path}: {exc}") from exc

    if not isinstance(raw, list):
        raise ValueError(f"Players file must contain a JSON array, got {type(raw).__name__}")

    configs: list[PlayerConfig] = []
    for i, entry in enumerate(raw):
        try:
            configs.append(PlayerConfig(**entry))
        except Exception as exc:
            raise ValueError(f"Invalid player config at index {i}: {exc}") from exc

    return configs
