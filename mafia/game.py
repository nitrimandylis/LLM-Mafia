import gc
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from openai import OpenAI

from mafia.events import EventLog, seat_color
from mafia.game_master import GameMaster, call_llm
from mafia.game_state import build_day_summary
from mafia.player import Player, Role, load_players_from_file


LM_STUDIO_URL = "http://localhost:1234/v1"
NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "qwen/qwen3.5-9b"
DEFAULT_NVIDIA_MODEL = "minimaxai/minimax-m3"
DEFAULT_CLAUDE_MODEL = "haiku"
DEFAULT_GM_MODEL = "qwen/qwen3.5-9b"


class MafiaGame:
    def __init__(
        self,
        reveal_secrets: bool = False,
        player_count: Optional[int] = None,
        max_workers: int = 4,
        model_override: Optional[str] = None,
        lm_studio_url: str = LM_STUDIO_URL,
        nvidia_api_key: Optional[str] = None,
        gm_model: Optional[str] = None,
        gm_enabled: bool = True,
        use_claude: bool = False,
    ):
        _root = Path(__file__).parent.parent
        base_players = load_players_from_file(str(_root / "players.json"))
        if not base_players:
            raise ValueError("No players could be loaded.")
        if player_count is not None:
            try:
                count = int(player_count)
            except Exception:
                count = len(base_players)
            count = max(4, min(count, len(base_players)))
            base_players = base_players[:count]

        self.use_nvidia = nvidia_api_key is not None
        self.use_claude = use_claude
        if self.use_claude:
            self.model = model_override or DEFAULT_CLAUDE_MODEL
            self._lm_client = None  # claude backend shells out, no HTTP client
        elif self.use_nvidia:
            self.model = model_override or DEFAULT_NVIDIA_MODEL
            self._lm_client = OpenAI(base_url=NVIDIA_API_URL, api_key=nvidia_api_key)
        else:
            self.model = model_override or DEFAULT_MODEL
            self._lm_client = OpenAI(base_url=lm_studio_url, api_key="lm-studio")

        self.players = [
            Player(p.name, personality=p.personality, model=p.model)
            for p in base_players
        ]
        self.day = 0
        self.game_log = []
        self.public_log = []
        self.events = EventLog()
        self.night_actions = {}
        self.private_notes: Dict[str, List[str]] = {}
        self.vote_history: List[Dict] = []
        self.night_kill_history: List[Dict] = []
        self.reveal_secrets = reveal_secrets
        self.max_workers = max_workers
        self.last_doctor_target: Optional[str] = None
        self.detective_investigated: set = set()
        self.day_summaries: Dict[int, str] = {}
        self.no_kill_nights = 0
        gm_model_resolved = gm_model or (
            self.model if (self.use_nvidia or self.use_claude) else DEFAULT_GM_MODEL
        )
        self.gm = GameMaster(
            client=self._lm_client,
            model=gm_model_resolved,
            use_nvidia=self.use_nvidia,
            enabled=gm_enabled,
            use_claude=self.use_claude,
        )

        try:
            with open(_root / "system_prompt.md", "r") as f:
                self.universal_prompt = f.read()
        except FileNotFoundError:
            print("ERROR: system_prompt.md not found. Using default prompt.")
            self.universal_prompt = "You are a player in a game of Mafia."

    def assign_roles(self):
        """Assign roles to players"""
        player_count = len(self.players)

        # Role distribution based on player count
        if player_count >= 10:
            mafia_count = 3
        elif player_count >= 7:
            mafia_count = 2
        else:
            mafia_count = 1

        # Shuffle and assign
        shuffled = self.players.copy()
        random.shuffle(shuffled)

        # Assign mafia
        for i in range(mafia_count):
            shuffled[i].role = Role.MAFIA

        # Assign detective and doctor if enough players
        if player_count >= 7:
            shuffled[mafia_count].role = Role.DETECTIVE
            shuffled[mafia_count + 1].role = Role.DOCTOR
        elif player_count >= 5:
            shuffled[mafia_count].role = Role.DETECTIVE

        # Rest are villagers
        for player in shuffled:
            if player.role is None:
                player.role = Role.VILLAGER

        self.log("\n🎭 ROLES ASSIGNED", "bold")
        for p in self.players:
            self.log(f"  {p.name}: {p.role.value}", "cyan", public=False)

    def get_mafia(self) -> List[Player]:
        """Return list of mafia players"""
        return [p for p in self.players if p.role == Role.MAFIA and p.alive]

    def get_alive_players(self) -> List[Player]:
        """Return list of alive players"""
        return [p for p in self.players if p.alive]

    def check_win_condition(self) -> Optional[str]:
        """Check if game is over. Returns 'mafia', 'town', or None"""
        alive = self.get_alive_players()
        mafia = self.get_mafia()

        if not mafia:
            return "town"

        if len(mafia) >= len(alive) - len(mafia):
            return "mafia"

        return None

    def day_phase(self):
        """Run day discussion phase with direct player interaction"""
        self.day += 1
        self.log(f"\n\n☀️  DAY {self.day} - TOWN MEETING", "bold")
        self.emit("phase", day=self.day, phase="day")

        alive = self.get_alive_players()
        alive_names = [p.name for p in alive]

        self.log(f"Alive players: {', '.join(alive_names)}", "yellow")

        last_kill = self.night_kill_history[-1] if self.night_kill_history else None
        last_vote = self.vote_history[-1] if self.vote_history else None
        gm_intro = self.gm.narrate_day_start(self.day, alive_names, last_kill, last_vote)
        if gm_intro:
            self.log(f"\n📜 {gm_intro}", "magenta")

        # Build context from recent events
        recent_context = build_day_summary(
            self.day, alive_names, self.vote_history, self.night_kill_history
        )

        day_statements: List[str] = []

        # DAY 1 SPECIAL HANDLING
        if self.day == 1:
            self.log(
                f"\n💬 Initial Impressions (No deaths yet, no prior behavior)", "cyan"
            )
            random.shuffle(alive)

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {}
                for player in alive:
                    others = [n for n in alive_names if n != player.name]
                    if player.role == Role.MAFIA:
                        # Never force mafia to open on a teammate
                        partners = {p.name for p in self.get_mafia()}
                        others = [n for n in others if n not in partners] or others
                    prompt = f"This is Day 1. No one has died yet. Based purely on first impressions, who seems suspicious? Pick ONE name from: {', '.join(random.sample(others, min(3, len(others))))}. Give a brief gut feeling (1 sentence). Do NOT reference past events or history."
                    future = executor.submit(
                        self.query_model,
                        player,
                        prompt,
                        "Day 1: No previous events. First discussion.",
                        min_words=5,
                        public_speech=True,
                    )
                    futures[future] = player

                for future in as_completed(futures):
                    player = futures[future]
                    response = future.result()
                    if response == f"*{player.name} remains silent*":
                        self.log(f"🗣️  {player.name} has nothing to say", "yellow", public=False)
                        continue
                    self.log(f"🗣️  {player.name}: {response}", "normal")
                    self.emit("statement", day=self.day, actor=player.name, text=response)
                    day_statements.append(f"{player.name}: {response}")
        else:
            # NORMAL DAY
            self.log(f"\n💬 Opening Statements", "cyan")
            random.shuffle(alive)

            # Build list of ELIMINATED players for context
            eliminated = [p.name for p in self.players if not p.alive]
            eliminated_str = (
                f"ELIMINATED (DO NOT ACCUSE): {', '.join(eliminated)}"
                if eliminated
                else "No eliminations yet"
            )

            # Build KEY FACTS from recent events (same for all players this round)
            key_facts_parts = []
            if self.night_kill_history:
                last_kill = self.night_kill_history[-1]
                if last_kill["saved"]:
                    key_facts_parts.append(f"Last night: {last_kill['victim']} was targeted by mafia but SAVED by the doctor.")
                else:
                    key_facts_parts.append(f"Last night: {last_kill['victim']} was killed (they were {last_kill['role']}).")
            if self.vote_history:
                last_vote = self.vote_history[-1]
                key_facts_parts.append(f"Yesterday: Town voted out {last_vote['eliminated']} (they were {last_vote['role']}).")

            key_facts = (" ".join(key_facts_parts) + " ") if key_facts_parts else ""

            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {}
                for player in alive:
                    others = [n for n in alive_names if n != player.name]
                    prompt = f"KEY FACTS: {key_facts}Day {self.day}. {eliminated_str}. Given these new facts, who among the ALIVE players is most suspicious? Reference specific past behavior from: {', '.join(others[:5])}."
                    future = executor.submit(
                        self.query_model, player, prompt, recent_context,
                        public_speech=True,
                    )
                    futures[future] = player

                for future in as_completed(futures):
                    player = futures[future]
                    response = future.result()
                    if response == f"*{player.name} remains silent*":
                        self.log(f"🗣️  {player.name} has nothing to say", "yellow", public=False)
                        continue
                    self.log(f"🗣️  {player.name}: {response}", "normal")
                    self.emit("statement", day=self.day, actor=player.name, text=response)
                    day_statements.append(f"{player.name}: {response}")

        # QUESTIONING ROUNDS (THIS WAS MISSING!)
        QUESTION_TEMPLATES = [
            "Ask {target} ONE direct question about their vote choices. Be specific (1 sentence).",
            "Challenge {target} on something suspicious they said or did. One direct question.",
            "Ask {target} to explain their behavior during yesterday's discussion. One sentence.",
            "Confront {target} about a moment where they seemed evasive. One direct question.",
            "Ask {target} who THEY most suspect and why. One sentence.",
            "Ask {target} to defend themselves against current suspicions. One direct question.",
        ]
        questioning_rounds = 2
        for round_num in range(questioning_rounds):
            self.log(
                f"\n❓ Questioning Round {round_num + 1}/{questioning_rounds}", "cyan"
            )

            random.shuffle(alive)

            # Each exchange runs to completion before the next starts: the
            # question is emitted before its answer is queried, so the answerer
            # (and every later asker) sees it in the shared transcript. Sequential
            # costs little real time — NVIDIA throttles globally and a single
            # local model serializes anyway — and reads as an actual conversation.
            for player in alive:
                others = [p for p in alive if p != player]
                if not others:
                    continue
                target = random.choice(others)

                recent_context = build_day_summary(
                    self.day, alive_names, self.vote_history, self.night_kill_history
                )
                template = QUESTION_TEMPLATES[(round_num + abs(hash(player.name))) % len(QUESTION_TEMPLATES)]
                question = self.query_model(
                    player, template.format(target=target.name), recent_context,
                    min_words=3, public_speech=True,
                )
                if question == f"*{player.name} remains silent*":
                    # Failed generation — skip the exchange, don't publish it
                    self.log(f"🔍 {player.name} has no question for {target.name}", "yellow", public=False)
                    continue
                self.log(f"🔍 {player.name} → {target.name}: {question}", "yellow")
                self.emit("question", day=self.day, actor=player.name, target=target.name, text=question)
                day_statements.append(f"{player.name} questions {target.name}: {question}")

                answer_prompt = f"{player.name} just asked you: '{question}'. Respond directly in 1-2 sentences."
                answer = self.query_model(target, answer_prompt, recent_context, public_speech=True)
                if answer == f"*{target.name} remains silent*":
                    self.log(f"💬 {target.name} does not answer", "normal", public=False)
                    continue
                self.log(f"💬 {target.name}: {answer}", "normal")
                self.emit("answer", day=self.day, actor=target.name, target=player.name, text=answer)
                day_statements.append(f"{target.name} answers {player.name}: {answer}")

        # FINAL ACCUSATIONS
        self.log(f"\n⚖️  Final Accusations", "cyan")
        random.shuffle(alive)

        eliminated = [p.name for p in self.players if not p.alive]
        eliminated_str = (
            f"DEAD/ELIMINATED: {', '.join(eliminated)}"
            if eliminated
            else "No deaths yet"
        )

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for player in alive:
                others = [n for n in alive_names if n != player.name]
                prompt = f"{eliminated_str}. Who should be eliminated TODAY from the ALIVE players? Choose from: {', '.join(others)}. Be decisive (1 sentence)."
                future = executor.submit(
                    self.query_model, player, prompt, build_day_summary(self.day, alive_names, self.vote_history, self.night_kill_history),
                    public_speech=True,
                )
                futures[future] = player

            # Collect everything BEFORE emitting: accusations are written
            # blind, so one early pick can't cascade into a dogpile (day 1
            # against the Detective was decided this way)
            collected = []
            for future in as_completed(futures):
                player = futures[future]
                response = future.result()
                if response == f"*{player.name} remains silent*":
                    self.log(f"⚔️  {player.name} offers no accusation", "yellow", public=False)
                    continue
                collected.append((player, response))

        for player, response in collected:
            self.log(f"⚔️  {player.name}: {response}", "red")
            accused = self.extract_vote(response, [n for n in alive_names if n != player.name])
            self.emit("accusation", day=self.day, actor=player.name, target=accused, text=response)
            day_statements.append(f"{player.name} accuses: {response}")

        # GM summarizes the day for injection into subsequent context
        summary = self.gm.narrate_day_summary(self.day, day_statements)
        if summary:
            self.day_summaries[self.day] = summary
            self.log(f"\n📋 Day {self.day} recap: {summary}", "cyan", public=False)

    def voting_phase(self) -> Optional[Player]:
        """Run voting phase and return eliminated player"""
        self.log(f"\n🗳️  VOTING PHASE", "bold")

        alive = self.get_alive_players()
        alive_names = [p.name for p in alive]

        # Build list of eliminated for context
        eliminated = [p.name for p in self.players if not p.alive]
        eliminated_str = (
            f"ELIMINATED (cannot vote for): {', '.join(eliminated)}"
            if eliminated
            else ""
        )

        recent_context = build_day_summary(
            self.day, alive_names, self.vote_history, self.night_kill_history
        )
        votes: Dict[str, str] = {}

        # Collect votes
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            for player in alive:
                valid_targets = [
                    n for n in alive_names if n != player.name
                ]  # CANNOT VOTE FOR SELF
                prompt = f"Vote to eliminate ONE player. {eliminated_str}. You CANNOT vote for yourself. Available: {', '.join(valid_targets)}. Reply with their name ONLY."
                future = executor.submit(
                    self.query_model, player, prompt, recent_context, min_words=1
                )
                futures[future] = (player, valid_targets)

            for future in as_completed(futures):
                player, valid_targets = futures[future]
                response = future.result()
                vote = self.extract_vote(response, valid_targets)

                # PREVENT SELF-VOTING
                if vote == player.name:
                    vote = None

                if vote:
                    votes[player.name] = vote
                    self.log(f"{player.name} votes: {vote}", "yellow")
                else:
                    # Random vote if parsing failed (but NOT self)
                    vote = random.choice(valid_targets)
                    votes[player.name] = vote
                    self.log(f"{player.name} votes: {vote} (default)", "yellow")

                self.emit("vote", day=self.day, actor=player.name, target=vote)

        # Count votes
        vote_counts: Dict[str, int] = {}
        for target in votes.values():
            vote_counts[target] = vote_counts.get(target, 0) + 1

        # Find eliminated player
        if not vote_counts:
            return None

        max_votes = max(vote_counts.values())
        tied = [name for name, count in vote_counts.items() if count == max_votes]

        eliminated_name = random.choice(tied) if len(tied) > 1 else tied[0]
        eliminated = next(p for p in alive if p.name == eliminated_name)

        eliminated.alive = False
        self.vote_history.append({
            "day": self.day,
            "eliminated": eliminated.name,
            "role": eliminated.role.value,
            "votes": dict(votes),
        })
        self.emit(
            "elimination",
            day=self.day,
            target=eliminated.name,
            role=eliminated.role.value,
            tally=dict(vote_counts),
        )

        gm_elim = self.gm.narrate_elimination(eliminated.name, eliminated.role.value, vote_counts)
        if gm_elim:
            self.log(f"\n📜 {gm_elim}", "magenta")
        else:
            self.log(
                f"\n💀 {eliminated.name} has been eliminated! They were: {eliminated.role.value}",
                "red",
            )

        return eliminated

    def night_phase(self):
        """Run night phase with mafia kill, detective investigation, doctor protection"""
        self.log(f"\n\n🌙 NIGHT {self.day}", "bold")
        self.emit("phase", day=self.day, phase="night")

        alive = self.get_alive_players()
        alive_names = [p.name for p in alive]
        mafia = self.get_mafia()

        recent_context = build_day_summary(
            self.day, alive_names, self.vote_history, self.night_kill_history
        )

        mafia_target = None
        detective_target = None
        doctor_target = None

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {}
            # Mafia chooses target
            if mafia:
                future = executor.submit(
                    self.mafia_conversation_and_choose_target,
                    mafia,
                    alive_names,
                    recent_context,
                )
                futures[future] = "mafia"

            # Detective investigates
            detectives = [p for p in alive if p.role == Role.DETECTIVE]
            if detectives:
                detective = detectives[0]
                uninvestigated = [n for n in alive_names if n != detective.name and n not in self.detective_investigated]
                valid = uninvestigated if uninvestigated else [n for n in alive_names if n != detective.name]
                prompt = f"Choose ONE player to investigate tonight. Pick someone suspicious from today's discussion. Targets: {', '.join(valid)}"
                future = executor.submit(
                    self.query_model, detective, prompt, recent_context, min_words=1
                )
                futures[future] = "detective"

            # Doctor protects
            doctors = [p for p in alive if p.role == Role.DOCTOR]
            if doctors:
                doctor = doctors[0]
                valid = alive_names
                last_protected = f" Last night you protected {self.last_doctor_target}." if self.last_doctor_target else ""
                prompt = f"Choose ONE player to protect tonight.{last_protected} Protecting different players each night is better strategy than always protecting yourself. Think about who spoke up most today or seemed targeted. Targets: {', '.join(valid)}"
                future = executor.submit(
                    self.query_model, doctor, prompt, recent_context, min_words=1
                )
                futures[future] = "doctor"

            for future in as_completed(futures):
                role = futures[future]
                result = future.result()

                if role == "mafia":
                    mafia_target = result
                elif role == "detective":
                    detective_target = self.extract_vote(
                        result, [n for n in alive_names if n != detectives[0].name]
                    )
                elif role == "doctor":
                    doctor_target = self.extract_vote(result, alive_names)
                    if doctor_target:
                        self.last_doctor_target = doctor_target

        # Post-night processing
        if detective_target:
            self.detective_investigated.add(detective_target)
            investigated = next(p for p in alive if p.name == detective_target)
            result = "MAFIA" if investigated.role == Role.MAFIA else "INNOCENT"
            note = f"Night {self.day}: Investigated {detective_target} - {result}"
            self.emit("investigation", private=True, day=self.day,
                      actor=detectives[0].name, target=detective_target, result=result)
            self.add_private_note(detectives[0], note)
            self.log(
                f"🔍 {detectives[0].name} investigated {detective_target}: {result}",
                "blue",
                public=False,
            )

        if doctor_target:
            self.emit("protection", private=True, day=self.day,
                      actor=doctors[0].name, target=doctor_target)
            self.log(
                f"🏥 {doctors[0].name} protected {doctor_target}",
                "green",
                public=False,
            )

        # Resolve night kill
        if mafia_target and mafia_target != doctor_target:
            victim = next(p for p in alive if p.name == mafia_target)
            victim.alive = False
            self.night_kill_history.append({
                "night": self.day,
                "victim": victim.name,
                "role": victim.role.value,
                "saved": False,
            })
            self.emit("night_kill", day=self.day, target=victim.name,
                      role=victim.role.value, saved=False)
            gm_kill = self.gm.narrate_night_kill(victim.name, saved=False)
            if gm_kill:
                self.log(f"\n📜 {gm_kill}", "magenta")
            else:
                self.log(f"\n💀 {victim.name} was killed during the night! They were: {victim.role.value}", "red")
        elif mafia_target and mafia_target == doctor_target:
            self.night_kill_history.append({
                "night": self.day,
                "victim": mafia_target,
                "role": next(p for p in self.players if p.name == mafia_target).role.value,
                "saved": True,
            })
            self.emit("save", day=self.day, target=mafia_target)
            gm_save = self.gm.narrate_night_kill(mafia_target, saved=True)
            if gm_save:
                self.log(f"\n📜 {gm_save}", "magenta")
            else:
                self.log(f"\n✨ The doctor's protection saved {doctor_target}!", "green")
        else:
            self.no_kill_nights += 1
            self.emit("night_no_kill", day=self.day)
            gm_quiet = self.gm.narrate_no_kill()
            if gm_quiet:
                self.log(f"\n📜 {gm_quiet}", "magenta")
            else:
                self.log(f"\n🌅 No one died during the night.", "green")

    def run(self):
        """Main game loop"""
        self.log("🎮 WELCOME TO LLM MAFIA", "bold")
        self.log(f"Players: {len(self.players)}", "cyan")

        # Assign roles
        self.assign_roles()

        # Structured event stream for the viewer. Roles only when spectating.
        self.emit(
            "game_start",
            players=[
                {
                    "name": p.name,
                    "seat": i,
                    "color": seat_color(i),
                    **({"role": p.role.value} if self.reveal_secrets else {}),
                }
                for i, p in enumerate(self.players)
            ],
            player_count=len(self.players),
        )

        # Game loop
        max_days = 10
        while self.day < max_days:
            # Day phase
            self.day_phase()

            # Check win before voting
            winner = self.check_win_condition()
            if winner:
                break

            # Voting
            self.voting_phase()

            # Check win after elimination
            winner = self.check_win_condition()
            if winner:
                break

            # Night phase
            self.night_phase()

            # Check win after night
            winner = self.check_win_condition()
            if winner:
                break

            # Garbage collect
            gc.collect()

        # Game over
        self.log("\n\n🏁 GAME OVER", "bold")
        survivors = [p.name for p in self.players if p.alive]
        self.emit("game_over", winner=winner or "timeout", survivors=survivors)
        if winner in ("town", "mafia"):
            gm_end = self.gm.narrate_game_over(winner, survivors, self.day)
            if gm_end:
                self.log(f"\n📜 {gm_end}", "magenta")
        if winner == "town":
            self.log("🎉 TOWN WINS! All mafia eliminated!", "green")
        elif winner == "mafia":
            self.log("😈 MAFIA WINS! They control the town!", "red")
        else:
            self.log("⏰ Game ended due to day limit", "yellow")

        # Reveal roles
        self.log("\n📋 FINAL ROLES:", "bold")
        for p in self.players:
            status = "💀" if not p.alive else "✅"
            self.log(f"  {status} {p.name}: {p.role.value}", "cyan")

        # Print stats
        stats = self.compute_stats()
        self.log("\n📊 GAME STATS:", "bold")
        self.log(f"  Days played: {stats['days']}", "cyan")
        self.log(f"  Night kills: {stats['night_kills']}  |  Doctor saves: {stats['successful_saves']}", "cyan")
        if stats["detective"]:
            d = stats["detective"]
            self.log(f"  Detective ({d['name']}): investigated {d['investigated']}, found mafia: {d['mafia_found']}", "cyan")
        self.log("  Vote accuracy:", "cyan")
        for name, ps in stats["players"].items():
            self.log(f"    {name} ({ps['role']}): {ps['vote_accuracy']} mafia votes correct", "cyan")

    def log(self, message: str, style: str = "normal", public: bool = True):
        """Print and store game events"""
        colors = {
            "normal": "\033[0m",
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "magenta": "\033[95m",
            "cyan": "\033[96m",
            "bold": "\033[1m",
        }
        if public or self.reveal_secrets:
            print(f"{colors.get(style, '')}{message}\033[0m")
        self.game_log.append(message)
        if public:
            self.public_log.append(message)

    def emit(self, type: str, private: bool = False, **fields):
        """Append a structured event. Private events are dropped unless reveal_secrets."""
        if private and not self.reveal_secrets:
            return
        self.events.emit(type, **fields)

    def add_private_note(self, player: Player, note: str):
        """Record something only this player knows (e.g. a detective result).
        Public actions live in the event stream — see render_public_transcript."""
        self.private_notes.setdefault(player.name, []).append(note)

    # Day-phase transcript budget: keep the last N spoken lines verbatim; older
    # history is carried by the GM day summaries. ponytail: flat cap, swap for
    # token counting only if a real budget ever bites.
    TRANSCRIPT_MAX_LINES = 40

    def render_public_transcript(self, day: int) -> str:
        """The current day's discussion as every player sees it, rendered from
        the public event stream (private events never reach self.events in a
        normal run). Capped at the last TRANSCRIPT_MAX_LINES."""
        lines: List[str] = []
        for e in self.events.to_list():
            if e.get("day") != day:
                continue
            t = e["type"]
            if t == "statement":
                lines.append(f"{e['actor']}: {e['text']}")
            elif t == "question":
                lines.append(f"{e['actor']} → {e['target']}: {e['text']}")
            elif t == "answer":
                lines.append(f"{e['actor']} (to {e['target']}): {e['text']}")
            elif t == "accusation":
                lines.append(f"{e['actor']} accuses: {e['text']}")
            elif t == "vote":
                lines.append(f"{e['actor']} votes {e['target']}")
        return "\n".join(lines[-self.TRANSCRIPT_MAX_LINES:])

    def build_context_for_player(self, player: Player, base_context: str) -> str:
        parts = []

        # Earlier days: compressed GM recaps (the current day is shown live below).
        prior = sorted((d, s) for d, s in self.day_summaries.items() if d < self.day)
        if prior:
            summary_block = "\n".join(f"Day {d}: {s}" for d, s in prior)
            parts.append(
                "=== EARLIER DAYS (recap) ===\n" + summary_block + "\n=== END RECAP ==="
            )

        # Today's discussion, public and shared by everyone reasoning right now.
        transcript = self.render_public_transcript(self.day)
        if transcript:
            # Mark the player's own lines so they don't mistake them for
            # someone else's opinion (HOLMES once recycled an anti-HOLMES
            # statement as his own opening)
            transcript = re.sub(
                rf"(?m)^{re.escape(player.name)}\b",
                f"{player.name} (YOU)",
                transcript,
            )
            parts.append(
                "=== TODAY'S DISCUSSION (public — everyone sees this) ===\n"
                + transcript
                + "\n=== END DISCUSSION ==="
            )

        # Structured facts: night kills, eliminations, who's alive.
        parts.append(base_context)

        # Only this player's private knowledge (e.g. detective findings).
        notes = self.private_notes.get(player.name)
        if notes:
            note_block = "\n".join(notes[-15:])
            parts.append(
                "=== YOUR PRIVATE KNOWLEDGE (only you know this) ===\n"
                + note_block
                + "\n=== END PRIVATE ==="
            )

        return "\n\n".join(parts)

    def _is_heading_line(self, line: str) -> bool:
        l = line.strip()
        if not l:
            return True
        l = re.sub(r"^[^\w]+", "", l).strip().lower()
        if not l:
            return True
        if re.match(r"^(day|night)\s*\d+\s*[-–—]", l):
            return True
        if "town meeting" in l and len(l.split()) <= 6:
            return True
        if re.match(r"^(discussion|voting)\s*(phase)?$", l) and len(l.split()) <= 3:
            return True
        return False

    def sanitize_response(self, player: Player, text: str) -> str:
        text = (text or "").strip()
        if not text:
            return ""

        # Strip internal reasoning blocks — these must never be visible to other players
        text = re.sub(r"<thinking>.*?</thinking>", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
        # Unterminated think block (truncated mid-reasoning): drop to end of text
        text = re.sub(r"<think(?:ing)?>.*$", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = text.strip()
        if not text:
            return ""

        # Clean up formatting
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        lines = [ln.rstrip() for ln in text.split("\n")]

        # Remove heading lines
        while lines and self._is_heading_line(lines[0]):
            lines.pop(0)

        text = "\n".join(lines).strip()

        # Remove self-referential prefixes
        name = re.escape(player.name)
        prefix_patterns = [
            rf"(?i)^\s*{name}\s*[:\-–—]\s*",
            rf"(?i)^\s*{name}\s+(?:says|said|asks|responds|replies)\s*:\s*",
        ]

        for pat in prefix_patterns:
            text = re.sub(pat, "", text).strip()

        # Stop at other player names
        other_names = [p.name for p in self.players if p.name != player.name]
        if other_names:
            pat = re.compile(
                rf"(?im)^\s*(?:{'|'.join(map(re.escape, other_names))})\s*:",
                re.MULTILINE,
            )
            m = pat.search(text)
            if m:
                text = text[: m.start()].rstrip()

        # Take first complete paragraph only
        paragraphs = text.split("\n\n")
        text = paragraphs[0].strip()

        # Clean up quotes and normalize spacing
        text = text.strip(" \t\\\"'`")
        text = " ".join(text.split())

        # KEEP COMPLETE SENTENCES - don't cut off at 3
        # Honorifics (DR. VANCE, Mr., Mrs., Ms., St.) are not sentence ends
        sentences = re.split(
            r"(?<!\bdr\.)(?<!\bmr\.)(?<!\bms\.)(?<!\bst\.)(?<!\bmrs\.)(?<=[.!?])\s+",
            text,
            flags=re.IGNORECASE,
        )

        # Only limit if we have TOO many sentences (>5)
        if len(sentences) > 5:
            return " ".join(sentences[:4]).strip()

        return text

    # Enforcement for the "NEVER reveal your role" rule: explicit first-person
    # self-labels only, scoped to the speaker's real role so persona speech
    # ("as a scientist", DR. VANCE's honorific) never trips it.
    ROLE_LEAK_PATTERNS = {
        Role.MAFIA: re.compile(
            r"\bas (?:a|the) mafia(?: member)?\b|\bi(?:'m| am) (?:a |the )?mafia\b"
            r"|\bmy fellow mafia\b|\bwe mafia\b|\bmy role is mafia\b"
            r"|\bmy mafia (?:partner|ally|allies|teammates?)\b",
            re.IGNORECASE,
        ),
        Role.DETECTIVE: re.compile(
            r"\bas (?:a|the) detective\b|\bi(?:'m| am) the detective\b"
            r"|\bmy role is detective\b",
            re.IGNORECASE,
        ),
        Role.DOCTOR: re.compile(
            r"\bas (?:a|the) doctor\b|\bi(?:'m| am) the doctor\b"
            r"|\bmy role is doctor\b",
            re.IGNORECASE,
        ),
    }

    def query_model(
        self,
        player: Player,
        prompt: str,
        context: str = "",
        min_words: int = 4,
        public_speech: bool = False,
    ) -> str:
        context = self.build_context_for_player(player, context)

        system_prompt = f"""{self.universal_prompt}

### YOUR PERSONALITY
You are {player.name}. {player.personality}

### YOUR ROLE
Your role is: {player.role.value}.
{"Your fellow mafia members are: " + ", ".join([p.name for p in self.get_mafia() if p.name != player.name]) + "." if player.role == Role.MAFIA and len(self.get_mafia()) > 1 else ""}

### CURRENT GAME STATE
Here is the game history so far:
{context if context.strip() else "No events yet. This is the start of the game."} """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Current task: {prompt}"},
        ]

        # players.json pins LM Studio/NVIDIA model IDs — meaningless to claude
        seat_model = self.model if self.use_claude else (player.model or self.model)
        try:
            self.log(f"  [Querying {seat_model}... ]", "cyan", public=False)
            start_time = time.time()

            response_text = self._call_backend(messages, model=seat_model)

            elapsed = time.time() - start_time
            tokens = len(response_text.split()) * 1.3
            tps = tokens / elapsed if elapsed > 0 else 0
            backend = "Claude" if self.use_claude else ("NVIDIA" if self.use_nvidia else "LM Studio")
            self.log(
                f"  [{backend}: {elapsed:.1f}s, ~{tps:.0f} tok/s]",
                "cyan",
                public=False,
            )

            response_text = self.sanitize_response(player, response_text)

            if not response_text or (
                min_words > 0 and len(response_text.split()) < min_words
            ):
                self.log(
                    f"  [empty/short reply from {seat_model} (reasoning may have consumed the budget) — retrying]",
                    "yellow", public=False,
                )
                retry_suffix = (
                    "Reply with a direct answer. No headings."
                    if min_words <= 1
                    else "Provide a concise 2-4 sentence answer. No headings."
                )
                retry_messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Current task: {prompt}\n\n{retry_suffix}"},
                ]
                response_text = self._call_backend(retry_messages, model=seat_model)
                response_text = self.sanitize_response(player, response_text)

            leak_re = self.ROLE_LEAK_PATTERNS.get(player.role) if public_speech else None
            if leak_re and response_text and leak_re.search(response_text):
                self.log(
                    f"  [role leak by {player.name} — re-querying]", "red", public=False
                )
                retry_messages = [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"Current task: {prompt}\n\nIMPORTANT: Your previous reply revealed your secret role. NEVER state your own role. Rewrite your reply without any mention of your role.",
                    },
                ]
                response_text = self.sanitize_response(
                    player, self._call_backend(retry_messages, model=seat_model)
                )
                if not response_text or leak_re.search(response_text):
                    response_text = f"*{player.name} mumbles something noncommittal*"

            if not response_text:
                response_text = f"*{player.name} remains silent*"
            return response_text

        except Exception as e:
            self.log(f"  [ERROR querying {seat_model}: {e}]", "red", public=False)
            return f"*{player.name} remains silent*"

    def _call_backend(self, messages: List[Dict], model: Optional[str] = None) -> str:
        # Reasoning is on (no /no_think): the budget must fit thinking AND the
        # spoken reply, and the thinking channel must stay private.
        return call_llm(
            self._lm_client, model or self.model, messages,
            use_nvidia=self.use_nvidia, schema_key="response",
            max_tokens=2048, private_reasoning=True,
            use_claude=self.use_claude,
            on_retry=lambda wait: self.log(
                f"  [429 rate limit — retrying in {wait:.0f}s]", "yellow", public=False
            ),
        )

    def extract_vote(self, response: str, valid_targets: List[str]) -> Optional[str]:
        response_lower = response.lower()
        name_map = {n.lower(): n for n in valid_targets}

        # Explicit vote-intent patterns tried first so "vote X because Y mentions Z" picks X not Z
        explicit_patterns = [
            r"\bvot(?:e|ing|ed)(?:\s+(?:for|out|to\s+eliminate))?\s+([\w][^\n,\.!?]{0,40})",
            r"\beliminate\s+([\w][^\n,\.!?]{0,40})",
            r"\bmy\s+vote\s+(?:is\s+)?(?:for\s+)?([\w][^\n,\.!?]{0,40})",
            r"\b([\w][^\n,\.!?]{0,40}?)\s+(?:is|gets)\s+my\s+vote\b",
            r"\bi\s+(?:would\s+)?(?:pick|choose|select|nominate)\s+(?:to\s+eliminate\s+)?([\w][^\n,\.!?]{0,40})",
        ]
        explicit_hits: List[Tuple[int, str]] = []
        for pat in explicit_patterns:
            for m in re.finditer(pat, response_lower):
                candidate = m.group(1).strip()
                for key, name in name_map.items():
                    if re.search(rf"\b{re.escape(key.split()[0])}\b", candidate):
                        explicit_hits.append((m.start(), name))
                        break
        if explicit_hits:
            explicit_hits.sort(key=lambda x: x[0])
            return explicit_hits[-1][1]

        # Fallback: last name mentioned anywhere in response
        all_hits: List[Tuple[int, str]] = []
        for key, name in name_map.items():
            for hit in re.finditer(rf"\b{re.escape(key)}\b", response_lower):
                all_hits.append((hit.start(), name))
        if all_hits:
            all_hits.sort(key=lambda x: x[0])
            return all_hits[-1][1]
        return None

    def parse_mafia_choice(
        self,
        response: str,
        valid_targets: List[str],
    ) -> Optional[str]:
        # A named target always wins: "CHEN — no one suspects her" is a kill
        # on CHEN, not a NO_KILL
        target = self.extract_vote(response, valid_targets)
        if target:
            return target
        rl = response.strip().lower()
        if re.search(
            r"\b(?:no[ _]?kill|nokill|skip|pass|nobody|no one|none|don'?t kill)\b", rl
        ):
            return "no_kill"
        return None

    def mafia_conversation_and_choose_target(
        self, mafia: List[Player], alive_names: List[str], context: str
    ) -> Optional[str]:
        if not mafia:
            return None

        mafia_names = [m.name for m in mafia]
        valid_targets = [n for n in alive_names if n not in mafia_names]
        if not valid_targets:
            return None

        if len(mafia) == 1:
            m = mafia[0]
            prompt = f"It's night. You are Mafia.\nChoose EXACTLY ONE of these targets: {', '.join(valid_targets)}\nOr choose NO_KILL.\nReply with ONLY the target name or NO_KILL."
            for attempt in range(3):
                resp = self.query_model(m, prompt, context, min_words=1)
                self.log(f"   (night reply: {resp[:120]})", "red", public=False)
                choice = self.parse_mafia_choice(resp, valid_targets)
                if choice:
                    if choice == "no_kill":
                        self.log("🌙 Mafia chose NO_KILL tonight", "red", public=False)
                        return None
                    return choice
            return random.choice(valid_targets)

        self.log("\n🤫 MAFIA WHISPER CHANNEL (private)", "red", public=False)
        chat: List[str] = []
        rounds = 2

        for r in range(rounds):
            self.log(f"   (round {r + 1}/{rounds})", "red", public=False)
            for m in mafia:
                chat_context = (
                    context
                    + "\n\nPrivate mafia chat so far:\n"
                    + ("\n".join(chat) if chat else "(no messages yet)")
                    + ""
                )
                if r == 0:
                    prompt = f"Mafia coordination: Suggest ONE target from this list: {', '.join(valid_targets)}. One sentence reason."
                else:
                    prompt = f"Mafia coordination: Based on the discussion, confirm or change your target. Choose from: {', '.join(valid_targets)}. Reply with name only or one sentence."
                try:
                    response = self.query_model(m, prompt, chat_context)
                    if response and "remains silent" not in response:
                        chat.append(f"{m.name}: {response}")
                        self.log(f"   {m.name}: {response}", "red", public=False)
                        self.emit("mafia_chat", private=True, day=self.day,
                                  actor=m.name, text=response)
                    else:
                        self.log(f"   {m.name}: [no response]", "red", public=False)
                except Exception as e:
                    self.log(f"   {m.name}: [error: {e}]", "red", public=False)

        # Final decision
        final_prompt = f"Final mafia vote. Choose ONE target from: {', '.join(valid_targets)}. Reply with the name ONLY."
        final_votes: Dict[str, int] = {}
        for m in mafia:
            response = self.query_model(m, final_prompt, "\n".join(chat), min_words=1)
            self.log(f"   ({m.name} final night vote: {response[:120]})", "red", public=False)
            voted_for = self.extract_vote(response, valid_targets)
            if voted_for:
                final_votes[voted_for] = final_votes.get(voted_for, 0) + 1

        if not final_votes:
            return random.choice(valid_targets)

        return max(final_votes, key=final_votes.get)

    def compute_stats(self) -> Dict:
        """Compute per-player vote accuracy, detective efficiency, and kill summary."""
        mafia_names = {p.name for p in self.players if p.role == Role.MAFIA}

        player_stats = {}
        for p in self.players:
            cast = [vh["votes"][p.name] for vh in self.vote_history if p.name in vh["votes"]]
            correct = sum(1 for t in cast if t in mafia_names)
            player_stats[p.name] = {
                "role": p.role.value if p.role else None,
                "survived": p.alive,
                "vote_accuracy": f"{correct}/{len(cast)}",
            }

        detective_stats = None
        det = next((p for p in self.players if p.role == Role.DETECTIVE), None)
        if det:
            found = [n for n in self.detective_investigated if n in mafia_names]
            detective_stats = {
                "name": det.name,
                "survived": det.alive,
                "investigated": sorted(self.detective_investigated),
                "mafia_found": found,
            }

        kills = [k for k in self.night_kill_history if not k["saved"]]
        saves = [k for k in self.night_kill_history if k["saved"]]
        return {
            "days": self.day,
            "players": player_stats,
            "detective": detective_stats,
            "night_kills": len(kills),
            "successful_saves": len(saves),
            "no_kill_nights": self.no_kill_nights,
        }
