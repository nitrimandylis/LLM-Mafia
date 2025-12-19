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
    model: str
    role: Optional[Role] = None
    alive: bool = True
    personality: str = ""


def load_players_from_file(
    file_path: str = "players.json", pro_mode: bool = False
) -> List[Player]:
    """Load player configurations from a JSON file."""
    try:
        with open(file_path, "r") as f:
            player_data = json.load(f)
        return [
            Player(
                name=p["name"],
                model="qwen3:4b" if pro_mode else "llama3.2:1b",
                personality=p["personality"],
            )
            for p in player_data
        ]
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading players from {file_path}: {e}")
        return []
