import json
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class Role(Enum):
    MAFIA = "Mafia"
    DOCTOR = "Doctor"
    DETECTIVE = "Detective"
    VILLAGER = "Villager"


@dataclass
class Player:
    name: str
    role: Optional[Role] = None
    alive: bool = True
    personality: str = ""
    model: Optional[str] = None  # per-seat override; None = game default


def load_players_from_file(file_path: str = "players.json") -> List[Player]:
    """Load player configurations from a JSON file."""
    try:
        with open(file_path, "r") as f:
            player_data = json.load(f)
        return [
            Player(name=p["name"], personality=p["personality"], model=p.get("model"))
            for p in player_data
        ]
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading players from {file_path}: {e}")
        return []
