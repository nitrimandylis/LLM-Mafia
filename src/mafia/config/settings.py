"""Application settings dataclass for LLM-Mafia."""
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppSettings:
    players_file: Path
    system_prompt_file: Path
    output_dir: Path
    max_days: int = 10
    memory_threshold_gb: float = 4.0
    max_workers: int = 4

    @classmethod
    def load_system_prompt(cls, path: Path) -> str:
        """Load system prompt text from file.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the file is empty.
        """
        resolved = Path(path)
        if not resolved.exists():
            raise FileNotFoundError(f"System prompt file not found: {path}")
        content = resolved.read_text(encoding="utf-8")
        if not content.strip():
            raise ValueError(f"System prompt file is empty: {path}")
        return content
