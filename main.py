import argparse
import json
import os
from dotenv import load_dotenv
from mafia.game import MafiaGame, LM_STUDIO_URL, DEFAULT_MODEL, DEFAULT_NVIDIA_MODEL, DEFAULT_CLAUDE_MODEL, DEFAULT_GM_MODEL

load_dotenv()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Mafia Game")
    parser.add_argument(
        "--reveal-secrets",
        action="store_true",
        help="Show private mafia conversations and detective results",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override model (default: qwen/qwen3.5-9b for LM Studio, minimaxai/minimax-m3 for NVIDIA)",
    )
    parser.add_argument(
        "--lm-studio-url",
        type=str,
        default=LM_STUDIO_URL,
        help=f"LM Studio base URL (default: {LM_STUDIO_URL})",
    )
    parser.add_argument(
        "--nvidia",
        action="store_true",
        help="Use NVIDIA NIM instead of LM Studio",
    )
    parser.add_argument(
        "--nvidia-key",
        type=str,
        default=None,
        help="NVIDIA API key (or set NVIDIA_API_KEY env var)",
    )
    parser.add_argument(
        "--claude",
        action="store_true",
        help=f"Use the claude CLI (subscription-billed) instead of LM Studio (default model: {DEFAULT_CLAUDE_MODEL})",
    )
    parser.add_argument(
        "--gm-model",
        type=str,
        default=None,
        help=f"Model for the Game Master narrator (default: {DEFAULT_GM_MODEL} for LM Studio, player model for NVIDIA)",
    )
    parser.add_argument(
        "--no-gm",
        action="store_true",
        help="Disable Game Master narration (saves API calls / speeds up games)",
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
        "--output", type=str, default="game_log.json", help="Output file for game log"
    )

    args = parser.parse_args()

    if args.claude and args.nvidia:
        print("❌ --claude and --nvidia are mutually exclusive")
        raise SystemExit(1)

    nvidia_key = None
    if args.nvidia:
        nvidia_key = args.nvidia_key or os.environ.get("NVIDIA_API_KEY")
        if not nvidia_key:
            print("❌ --nvidia requires an API key via --nvidia-key or NVIDIA_API_KEY env var")
            raise SystemExit(1)

    print("🎭 INITIALIZING LLM MAFIA GAME...\n")
    if args.claude:
        model = args.model  # None → seats cycle haiku/sonnet/opus, GM on sonnet
        max_workers = args.max_workers
        seat_desc = model or "haiku/sonnet/opus mix"
        print(f"🔌 Backend: Claude CLI  |  Model: {seat_desc}  |  Workers: {max_workers}\n")
    elif args.nvidia:
        model = args.model or DEFAULT_NVIDIA_MODEL
        max_workers = args.max_workers if args.max_workers != 4 else 2
        print(f"🔌 Backend: NVIDIA NIM  |  Model: {model}  |  Workers: {max_workers}\n")
    else:
        model = args.model or DEFAULT_MODEL
        max_workers = args.max_workers
        print(f"🔌 Backend: LM Studio ({args.lm_studio_url})  |  Model: {model}\n")

    game = MafiaGame(
        reveal_secrets=args.reveal_secrets,
        player_count=args.player_count,
        max_workers=max_workers,
        model_override=model,
        lm_studio_url=args.lm_studio_url,
        nvidia_api_key=nvidia_key,
        gm_model=args.gm_model,
        gm_enabled=not args.no_gm,
        use_claude=args.claude,
    )

    try:
        game.run()

        stats = game.compute_stats()
        with open(args.output, "w") as f:
            json.dump(
                {
                    "events": game.events.to_list(),
                    "game_log": game.game_log,
                    "public_log": game.public_log,
                    "day": game.day,
                    "stats": stats,
                },
                f,
                indent=2,
            )
        print(f"\n📝 Game log saved to {args.output}")

    except KeyboardInterrupt:
        print("\n\n⚠️  Game interrupted by user")
    except Exception as e:
        print(f"\n❌ Game crashed: {e}")
