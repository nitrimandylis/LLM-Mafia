import argparse
import json
import os

from dotenv import load_dotenv

from game import MafiaGame

load_dotenv()


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
        "--model",
        type=str,
        default=None,
        help="Override model for all players (e.g. llama3.2:1b, qwen3:4b)",
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
    parser.add_argument(
        "--nvidia",
        action="store_true",
        help="Use NVIDIA NIM endpoint instead of local Ollama",
    )
    parser.add_argument(
        "--nvidia-key",
        type=str,
        default=None,
        help="NVIDIA API key (falls back to NVIDIA_API_KEY env var)",
    )
    parser.add_argument(
        "--nvidia-model",
        type=str,
        default=None,
        help="NVIDIA NIM model to use (e.g. moonshotai/kimi-k2.5, meta/llama-3.3-70b-instruct)",
    )

    args = parser.parse_args()

    # Resolve NVIDIA key
    nvidia_key = args.nvidia_key or os.environ.get("NVIDIA_API_KEY")
    if args.nvidia and not nvidia_key:
        print("❌ --nvidia requires an API key via --nvidia-key or NVIDIA_API_KEY env var")
        raise SystemExit(1)

    # --nvidia-model takes precedence over --model when using NVIDIA backend
    model = (args.nvidia_model if args.nvidia else None) or args.model

    # Create and run the game
    print("🎭 INITIALIZING LLM MAFIA GAME...\n")
    if args.nvidia:
        print(f"🔌 Backend: NVIDIA NIM  |  Model: {model or 'moonshotai/kimi-k2.5'}\n")
    else:
        print(f"🔌 Backend: Ollama\n")

    game = MafiaGame(
        reveal_secrets=args.reveal_secrets,
        player_count=args.player_count,
        pro_mode=args.pro_mode,
        max_workers=args.max_workers,
        memory_threshold=args.memory_threshold,
        model_override=model,
        use_nvidia=args.nvidia,
        nvidia_api_key=nvidia_key,
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
