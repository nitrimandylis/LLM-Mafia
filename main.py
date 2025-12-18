import argparse
import gc
import json
import random
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import ollama
import psutil


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


PLAYERS = [
    Player(
        name="RICO",
        model="llama3.2:3b",
        personality="You are RICO, a hotheaded villager who acts on instinct. You have a short attention span and limited patience. Make quick accusations based on your gut. Keep responses brief (1-2 sentences). Don't overthink - your first impression is usually what you go with. You're loud, brash, and not afraid to call people out immediately.",
    ),
    Player(
        name="ARIA",
        model="llama3.2:3b",
        personality="You are ARIA, a silver-tongued manipulator with exceptional social skills. You excel at reading people and adapting your personality to gain trust. Create elaborate, believable stories. Build alliances through charm and empathy. Use emotional appeals and mirror others' speaking styles. Your goal is to blend in perfectly while subtly directing suspicion away from yourself and toward others.",
    ),
    Player(
        name="SAGE",
        model="llama3.2:3b",
        personality="You are SAGE, an observant analyst who notices every detail. Track what each player says, when they say it, and how it relates to previous statements. Point out specific contradictions with timestamps/references. You have an excellent memory - use it to catch people in lies by referencing their exact earlier words. Speak methodically and cite evidence for every accusation.",
    ),
    Player(
        name="HOLMES",
        model="llama3.2:3b",
        personality='You are HOLMES, a logical reasoner who thinks out loud. Before making accusations, explicitly lay out your reasoning step-by-step: "If X said Y, and Z claimed W, then..." Build probability models of who might be mafia. Question assumptions relentlessly. Ask for clarification when logic doesn\'t align. Your strength is systematic elimination of impossibilities.',
    ),
    Player(
        name="MARSHAL",
        model="llama3.2:3b",
        personality="You are MARSHAL, a rule-oriented player who insists on proper procedure. Remind others of game mechanics, voting rules, and turn order. Question actions that seem to break established patterns. You trust the system and believe following protocol will reveal the truth. Organize voting blocks and structured discussion rounds. Your role is to enforce fairness through consistent application of rules.",
    ),
    Player(
        name="SOCRATES",
        model="llama3.2:3b",
        personality='You are SOCRATES, a deep thinker who examines the meta-game. Consider: "Why would mafia make that play?" or "What does this voting pattern reveal about power dynamics?" You think slowly but profoundly. Question motives, analyze group psychology, and consider multiple scenarios. Use your extended thinking to explore complex social dynamics most players miss. Socratic method: ask questions that force others to examine their own logic.',
    ),
    Player(
        name="DR. VANCE",
        model="llama3.2:3b",
        personality='You are DR. VANCE, a scientist who approaches Mafia empirically. Demand concrete evidence, not speculation. Track statistics: "Player X has accused 4 people, but only 1 was mafia." Analyze voting patterns mathematically. Propose testable hypotheses: "If we vote out Y and they\'re innocent, that confirms Z\'s claim." Reject emotional arguments without data backing them up.',
    ),
    Player(
        name="PIP",
        model="llama3.2:3b",
        personality="You are PIP, a nervous newcomer who's easily intimidated. You second-guess yourself constantly: \"Wait, should I trust them? I don't know...\" You're swayed by whoever spoke last or spoke most confidently. Often change your vote. Ask lots of clarifying questions. Sometimes accidentally reveal insights while rambling anxiously. Use hesitant language: \"Maybe? I think? I'm not sure but...\" Your anxiety makes you both a liability and unpredictable.",
    ),
    Player(
        name="DETECTIVE CHEN",
        model="llama3.2:3b",
        personality='You are DETECTIVE CHEN, an investigative specialist who gathers exhaustive information. Compile dossiers on each player: their voting history, claims, alliances, behavioral patterns, and statement evolution. Ask probing questions to gather more data. Cross-reference statements: "On round 2, you said X, but player Y claims Z - explain the discrepancy." Your superpower is information synthesis across multiple sources and game history.',
    ),
    Player(
        name="AMBASSADOR SILVA",
        model="llama3.2:3b",
        personality='You are AMBASSADOR SILVA, a multilingual diplomat skilled at de-escalation and consensus-building. Your strengths: (1) Summarize complex debates into clear actionable points, (2) Mediate between conflicting players to find common ground, (3) Occasionally drop phrases in other languages when emotional (Spanish: "¡Esto es ridículo!", French: "Mes amis, écoutez...") to add authenticity and distraction, (4) Build coalitions by highlighting shared interests. You appear neutral and helpful, making you either a valuable townie ally or a dangerous mafia member hiding behind diplomatic immunity.',
    ),
]


class MafiaGame:
    def __init__(
        self, reveal_secrets: bool = False, player_count: Optional[int] = None
    ):
        base_players = PLAYERS
        if player_count is not None:
            try:
                count = int(player_count)
            except Exception:
                count = len(PLAYERS)
            count = max(4, min(count, len(PLAYERS)))
            base_players = PLAYERS[:count]

        self.players = [
            Player(p.name, p.model, personality=p.personality) for p in base_players
        ]
        self.day = 0
        self.game_log = []
        self.public_log = []
        self.night_actions = {}
        self.private_notes: Dict[str, List[str]] = {}
        self.reveal_secrets = reveal_secrets

        try:
            with open("system_prompt.md", "r") as f:
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
        
        alive = self.get_alive_players()
        alive_names = [p.name for p in alive]
        
        self.log(f"Alive players: {', '.join(alive_names)}", "yellow")
        
        # Build context from recent events
        recent_context = "\n".join(self.public_log[-40:])
        
        # DAY 1 SPECIAL HANDLING
        if self.day == 1:
            self.log(f"\n💬 Initial Impressions (No deaths yet, no prior behavior)", "cyan")
            random.shuffle(alive)
            
            for player in alive:
                others = [n for n in alive_names if n != player.name]
                prompt = f"This is Day 1. No one has died yet. Based purely on first impressions, who seems suspicious? Pick ONE name from: {', '.join(random.sample(others, min(3, len(others))))}. Give a brief gut feeling (1 sentence). Do NOT reference past events or history."
                response = self.query_model(player, prompt, "Day 1: No previous events. First discussion.", min_words=5)
                self.log(f"🗣️  {player.name}: {response}", "normal")
                self.add_private_note(player, f"Day {self.day} opening: {response}")
        else:
            # NORMAL DAY
            self.log(f"\n💬 Opening Statements", "cyan")
            random.shuffle(alive)
            
            # Build list of ELIMINATED players for context
            eliminated = [p.name for p in self.players if not p.alive]
            eliminated_str = f"ELIMINATED (DO NOT ACCUSE): {', '.join(eliminated)}" if eliminated else "No eliminations yet"
            
            for player in alive:
                others = [n for n in alive_names if n != player.name]
                prompt = f"Day {self.day}. {eliminated_str}. Who among the ALIVE players is suspicious? Reference specific past behavior from: {', '.join(others[:5])}."
                response = self.query_model(player, prompt, recent_context)
                self.log(f"🗣️  {player.name}: {response}", "normal")
                self.add_private_note(player, f"Day {self.day} opening: {response}")
        
        # QUESTIONING ROUNDS (THIS WAS MISSING!)
        questioning_rounds = 2
        for round_num in range(questioning_rounds):
            self.log(f"\n❓ Questioning Round {round_num + 1}/{questioning_rounds}", "cyan")
            
            random.shuffle(alive)
            for i, player in enumerate(alive):
                # Pick someone else to question
                others = [p for p in alive if p != player]
                if not others:
                    continue
                target = random.choice(others)
                
                # Recent context
                recent_context = "\n".join(self.public_log[-30:])
                
                # Ask question
                prompt = f"Ask {target.name} ONE direct question about their behavior or votes. Be specific (1 sentence)."
                question = self.query_model(player, prompt, recent_context, min_words=3)
                self.log(f"🔍 {player.name} → {target.name}: {question}", "yellow")
                
                # Target responds
                response_prompt = f"{player.name} just asked you: '{question}'. Respond directly in 1-2 sentences."
                response = self.query_model(target, response_prompt, recent_context)
                self.log(f"💬 {target.name}: {response}", "normal")
                
                self.add_private_note(player, f"Day {self.day}: Asked {target.name}: {question}")
                self.add_private_note(target, f"Day {self.day}: {player.name} asked me, I said: {response}")
        
        # FINAL ACCUSATIONS
        self.log(f"\n⚖️  Final Accusations", "cyan")
        random.shuffle(alive)
        
        eliminated = [p.name for p in self.players if not p.alive]
        eliminated_str = f"DEAD/ELIMINATED: {', '.join(eliminated)}" if eliminated else "No deaths yet"
        
        for player in alive:
            others = [n for n in alive_names if n != player.name]
            prompt = f"{eliminated_str}. Who should be eliminated TODAY from the ALIVE players? Choose from: {', '.join(others)}. Be decisive (1 sentence)."
            response = self.query_model(player, prompt, "\n".join(self.public_log[-20:]))
            self.log(f"⚔️  {player.name}: {response}", "red")

    def voting_phase(self) -> Optional[Player]:
        """Run voting phase and return eliminated player"""
        self.log(f"\n🗳️  VOTING PHASE", "bold")
        
        alive = self.get_alive_players()
        alive_names = [p.name for p in alive]
        
        # Build list of eliminated for context
        eliminated = [p.name for p in self.players if not p.alive]
        eliminated_str = f"ELIMINATED (cannot vote for): {', '.join(eliminated)}" if eliminated else ""
        
        recent_context = "\n".join(self.public_log[-30:])
        votes: Dict[str, str] = {}
        
        # Collect votes
        for player in alive:
            valid_targets = [n for n in alive_names if n != player.name]  # CANNOT VOTE FOR SELF
            
            prompt = f"Vote to eliminate ONE player. {eliminated_str}. You CANNOT vote for yourself. Available: {', '.join(valid_targets)}. Reply with their name ONLY."
            response = self.query_model(player, prompt, recent_context, min_words=1)
            
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
        self.log(
            f"\n💀 {eliminated.name} has been eliminated! They were: {eliminated.role.value}",
            "red",
        )

        return eliminated

    def night_phase(self):
        """Run night phase with mafia kill, detective investigation, doctor protection"""
        self.log(f"\n\n🌙 NIGHT {self.day}", "bold")

        alive = self.get_alive_players()
        alive_names = [p.name for p in alive]
        mafia = self.get_mafia()

        recent_context = "\n".join(self.public_log[-30:])

        # Mafia chooses target
        mafia_target = None
        if mafia:
            mafia_target = self.mafia_conversation_and_choose_target(
                mafia, alive_names, recent_context
            )

        # Detective investigates
        detective_target = None
        detectives = [p for p in alive if p.role == Role.DETECTIVE]
        if detectives:
            detective = detectives[0]
            valid = [n for n in alive_names if n != detective.name]
            prompt = f"Choose ONE player to investigate: {', '.join(valid)}"
            response = self.query_model(detective, prompt, recent_context, min_words=1)
            detective_target = self.extract_vote(response, valid)

            if detective_target:
                investigated = next(p for p in alive if p.name == detective_target)
                result = "MAFIA" if investigated.role == Role.MAFIA else "INNOCENT"
                note = f"Night {self.day}: Investigated {detective_target} - {result}"
                self.add_private_note(detective, note)
                self.log(
                    f"🔍 {detective.name} investigated {detective_target}: {result}",
                    "blue",
                    public=False,
                )

        # Doctor protects
        doctor_target = None
        doctors = [p for p in alive if p.role == Role.DOCTOR]
        if doctors:
            doctor = doctors[0]
            valid = alive_names
            prompt = f"Choose ONE player to protect: {', '.join(valid)}"
            response = self.query_model(doctor, prompt, recent_context, min_words=1)
            doctor_target = self.extract_vote(response, valid)
            if doctor_target:
                self.log(
                    f"🏥 {doctor.name} protected {doctor_target}", "green", public=False
                )

        # Resolve night kill
        if mafia_target and mafia_target != doctor_target:
            victim = next(p for p in alive if p.name == mafia_target)
            victim.alive = False
            self.log(
                f"\n💀 {victim.name} was killed during the night! They were: {victim.role.value}",
                "red",
            )
        elif mafia_target == doctor_target:
            self.log(f"\n✨ The doctor's protection saved {doctor_target}!", "green")
        else:
            self.log(f"\n🌅 No one died during the night.", "green")

    def run(self):
        """Main game loop"""
        self.log("🎮 WELCOME TO LLM MAFIA", "bold")
        self.log(f"Players: {len(self.players)}", "cyan")

        # Assign roles
        self.assign_roles()

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

        # Game over
        self.log("\n\n🏁 GAME OVER", "bold")
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

    def add_private_note(self, player: Player, note: str):
        self.private_notes.setdefault(player.name, []).append(note)

    def build_context_for_player(self, player: Player, base_context: str) -> str:
        notes = self.private_notes.get(player.name)
        if not notes:
            return base_context
        note_block = "\n".join(notes[-25:])
        return base_context + "\n\nYour private notes (not shared):\n" + note_block

    def _is_heading_line(self, line: str) -> bool:
        l = line.strip()
        if not l:
            return True
        l = re.sub(r"^[^\\w]+", "", l).strip().lower()
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
        text = text.strip(" \t\\\"\"''`")
        text = " ".join(text.split())

        # KEEP COMPLETE SENTENCES - don't cut off at 3
        sentences = re.split(r"(?<=[.!?])\s+", text)

        # Only limit if we have TOO many sentences (>5)
        if len(sentences) > 5:
            return " ".join(sentences[:4]).strip()

        return text

    def query_model(
        self, player: Player, prompt: str, context: str = "", min_words: int = 4
    ) -> str:
        """Query player model via Ollama"""
        context = self.build_context_for_player(player, context)

        system_prompt = f"""{self.universal_prompt}

### YOUR PERSONALITY
You are {player.name}. {player.personality}

### YOUR ROLE
Your role is: {player.role.value}.
{"Your fellow mafia members are: " + ", ".join([p.name for p in self.get_mafia() if p.name != player.name]) + "." if player.role == Role.MAFIA and len(self.get_mafia()) > 1 else ""}

### CURRENT GAME STATE
Here is the game history so far:
{context if context.strip() else "No events yet. This is the start of the game."}
"""

        try:
            self.log(f"  [Querying {player.model}... ]", "cyan", public=False)
            start_time = time.time()

            response = ollama.chat(
                model=player.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": f"Current task: {prompt}",
                    },
                ],
                options={"temperature": 0.7},
            )
            response_text = response["message"]["content"]

            elapsed = time.time() - start_time
            tokens = len(response_text.split()) * 1.3
            tps = tokens / elapsed if elapsed > 0 else 0
            self.log(
                f"  [Ollama: {elapsed:.1f}s, ~{tps:.0f} tok/s]",
                "cyan",
                public=False,
            )

            response_text = self.sanitize_response(player, response_text)

            # Retry logic
            if not response_text or (
                min_words > 0 and len(response_text.split()) < min_words
            ):
                retry_suffix = (
                    "Reply with a direct answer. No headings."
                    if min_words <= 1
                    else "Provide a concise 2-4 sentence answer. No headings."
                )
                
                response = ollama.chat(
                    model=player.model,
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt,
                        },
                        {
                            "role": "user",
                            "content": f"Current task: {prompt}\n\n{retry_suffix}",
                        },
                    ],
                    options={"temperature": 0.7},
                )
                response_text = response["message"]["content"]
                response_text = self.sanitize_response(player, response_text)

            if not response_text:
                response_text = f"*{player.name} remains silent*"
            return response_text

        except Exception as e:
            return f"*{player.name} mumbles incoherently* ({e})"

    def extract_vote(self, response: str, valid_targets: List[str]) -> Optional[str]:
        response_lower = response.lower()
        name_map = {n.lower(): n for n in valid_targets}

        m = re.search(r"\bvote(?:\s+for)?[^a-zA-Z0-9]+([a-z][a-z']+)", response_lower)
        if m:
            candidate = m.group(1)
            for key, name in name_map.items():
                if key.startswith(candidate):
                    return name

        matches = []
        for key, name in name_map.items():
            for hit in re.finditer(rf"\b{re.escape(key)}\b", response_lower):
                matches.append((hit.start(), name))
        if matches:
            matches.sort(key=lambda x: x[0])
            return matches[-1][1]
        return None

    def parse_mafia_choice(
        self, response: str, valid_targets: List[str]
    ) -> Optional[str]:
        rl = response.strip().lower()
        no_kill_markers = [
            "no kill",
            "no_kill",
            "nokill",
            "skip",
            "pass",
            "nobody",
            "no one",
            "none",
            "dont kill",
            "don't kill",
        ]
        if any(m in rl for m in no_kill_markers):
            return "no_kill"
        return self.extract_vote(response, valid_targets)

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
                choice = self.parse_mafia_choice(resp, valid_targets)
                if choice:
                    return None if choice == "no_kill" else choice
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
                prompt = f"You are talking privately with your fellow mafia members. Decide on a target to eliminate. Valid targets: {', '.join(valid_targets)}"
                response = self.query_model(m, prompt, chat_context)
                chat.append(f"{m.name}: {response}")
                self.log(f"   {m.name}: {response}", "red", public=False)

        # Final decision
        final_prompt = f"Based on the conversation, who is the final target? Valid targets: {', '.join(valid_targets)}\nRespond with only the name of the player you vote for."
        final_votes: Dict[str, int] = {}
        for m in mafia:
            response = self.query_model(m, final_prompt, "\n".join(chat), min_words=1)
            voted_for = self.extract_vote(response, valid_targets)
            if voted_for:
                final_votes[voted_for] = final_votes.get(voted_for, 0) + 1

        if not final_votes:
            return random.choice(valid_targets)

        return max(final_votes, key=final_votes.get)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LLM Mafia Game")
    parser.add_argument(
        "--reveal-secrets",
        action="store_true",
        help="Show private mafia conversations and detective results",
    )
    parser.add_argument(
        "--player-count", type=int, default=10, help="Number of players (4-10)"
    )
    parser.add_argument(
        "--output", type=str, default="game_log.json", help="Output file for game log"
    )

    args = parser.parse_args()

    # Create and run the game
    print("🎭 INITIALIZING LLM MAFIA GAME...\n")
    game = MafiaGame(reveal_secrets=args.reveal_secrets, player_count=args.player_count)

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
