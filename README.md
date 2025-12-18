# LLM Mafia Game

This is an LLM-powered Mafia game where each player is controlled by a language model. Players interact, discuss, accuse, and vote to eliminate each other, trying to uncover the Mafia hidden among them.

## Setup

1.  **Install Ollama:**
    Follow the instructions on [Ollama's website](https://ollama.com/) to install Ollama for your operating system.

2.  **Pull Models:**
    The game currently uses the `llama3.2:3b` model. Pull it using Ollama:
    ```bash
    ollama pull llama3.2:3b
    ```

3.  **Install Dependencies:**
    It's recommended to create a virtual environment first:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

## How to Run

To start the game, run `main.py`:

```bash
python main.py [OPTIONS]
```

**Options:**

*   `--reveal-secrets`: Show private mafia conversations and detective results.
*   `--player-count <int>`: Number of players (4-10). Defaults to 10.
*   `--output <filename>`: Output file for the game log (e.g., `game_log.json`). Defaults to `game_log.json`.

**Example:**

```bash
python main.py --player-count 7 --output my_mafia_game.json
```

## Recent Changes

*   **Improved Day Phase:** Added questioning rounds for more dynamic player interaction.
*   **Prevented Self-Voting:** Players can no longer vote for themselves.
*   **Model Upgrade:** All players now use the more capable `llama3.2:3b` model to improve game context understanding and reduce "hallucinations."
*   **Performance Optimization (Planned):** Future updates will focus on parallelizing model queries to significantly speed up gameplay.

---
Enjoy the game!
