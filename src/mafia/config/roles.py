"""Role enum and role distribution logic."""
from enum import Enum


class Role(Enum):
    MAFIA = "Mafia"
    DOCTOR = "Doctor"
    DETECTIVE = "Detective"
    VILLAGER = "Villager"


def get_role_distribution(player_count: int) -> dict[Role, int]:
    """Return {Role: count} based on player count.

    Rules:
      - >=10 players: 3 mafia
      - >=7  players: 2 mafia + 1 detective + 1 doctor
      - >=5  players: 1 mafia + 1 detective
      - <5   players: 1 mafia
    Rest are villagers.

    Raises:
        ValueError: If player_count < 1.
    """
    if player_count < 1:
        raise ValueError(f"player_count must be >= 1, got {player_count}")

    if player_count >= 10:
        mafia = 3
        detective = 1
        doctor = 1
    elif player_count >= 7:
        mafia = 2
        detective = 1
        doctor = 1
    elif player_count >= 5:
        mafia = 1
        detective = 1
        doctor = 0
    else:
        mafia = 1
        detective = 0
        doctor = 0

    special = mafia + detective + doctor
    villagers = max(0, player_count - special)

    distribution: dict[Role, int] = {
        Role.MAFIA: mafia,
        Role.VILLAGER: villagers,
    }
    if detective:
        distribution[Role.DETECTIVE] = detective
    if doctor:
        distribution[Role.DOCTOR] = doctor

    return distribution
