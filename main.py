import argparse
import json
from game import MafiaGame


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Mafia Game")
    parser.add_argument(
        "--reveal-secrets",
        action="store_true",
        help="Show private mafia conversations and detective results",
    )
    parser.add_argument(
        "--pro-mode", action="store_true", help="Use a more advanced model for players"
    )
    parser.add_argument(
        "--player-count", type=int, default=10, help="Number of players (4-10)"
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum number of parallel workers for model queries",
    )
    parser.add_argument(
        "--memory-threshold",
        type=int,
        default=4,
        help="Minimum free RAM (in GB) required to run a model",
    )
    parser.add_argument(
        "--output", type=str, default="game_log.json", help="Output file for game log"
    )

    args = parser.parse_args()

    # Create and run the game
    print("🎭 INITIALIZING LLM MAFIA GAME...\n")
    game = MafiaGame(
        reveal_secrets=args.reveal_secrets,
        player_count=args.player_count,
        pro_mode=args.pro_mode,
        max_workers=args.max_workers,
        memory_threshold=args.memory_threshold,
    )

    # Start the game
    try:
        game.run()

        # Save game log
        with open(args.output, "w") as f:
            json.dump(
                {
                    "game_log": game.game_log,
                    "public_log": game.public_log,
                    "day": game.day,
                },
                f,
                indent=2,
            )
        print(f"\n📝 Game log saved to {args.output}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Game interrupted by user")
    except Exception as e:
        print(f"\n❌ Game crashed: {e}")
