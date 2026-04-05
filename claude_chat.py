#!/usr/bin/env python3
# claude_chat.py
# Terminal chat interface to Claude API for Arachnet project development.
# Designed for use with screen readers (Orca, VoiceOver).
#
# Place this file in the project root: ~/project_embeddings/claude_chat.py
# Always run from the project root with venv active:
#   cd ~/project_embeddings
#   source venv/bin/activate
#   python claude_chat.py --session myproject
#
# Transcripts are written to log/ under the project root (next to this file).
# Session JSON files are stored in ~/.claude_sessions/
# Extracted files are written relative to the project root (current dir).
#
# Requirements:
#   pip install anthropic
#   export ANTHROPIC_API_KEY="your-key-here"  # in .bashrc
#
# Usage:
#   python claude_chat.py                         # anonymous session
#   python claude_chat.py --session myproject     # named persistent session
#   python claude_chat.py --session myproject --file docs/project_summary.md
#
# Commands during chat:
#   /quit or /q        -- save session and exit
#   /clear             -- clear history, start fresh (session file kept)
#   /save              -- save session and write transcript now
#   /history           -- show number of turns and session name
#   /sessions          -- list all saved sessions
#   /file <path>       -- load file into next message
#   /extract <path>    -- extract named file block from last transcript
#
# When asking Claude to produce a file, tell him to use this format:
#   === BEGIN FILE: path/to/file.py ===
#   ... content ...
#   === END FILE: path/to/file.py ===
# Then: /save  followed by  /extract path/to/file.py
#
# Error handling:
#   Startup errors (missing API key, bad --file) exit cleanly.
#   Session errors (bad /file path, save failure, API errors) are
#   reported and the session continues. Context is never lost.
#
# Last modified: 2026-04-05

import anthropic
import argparse
import datetime
import json
import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096

# Project root is the directory containing this script.
# Transcripts go to PROJECT_ROOT/log/
PROJECT_ROOT = Path(__file__).resolve().parent
LOG_DIR = PROJECT_ROOT / "log"
SESSIONS_DIR = Path.home() / ".claude_sessions"

SYSTEM_PROMPT = (
    "You are assisting Jan Mura with developing the Arachnet Clinical "
    "Embeddings project -- a SNOMED CT terminology embedding platform built "
    "on Oracle 23ai. The project uses Python, Bash, YAML, and Oracle SQL. "
    "Jan is blind and works in a terminal with Orca screen reader on Ubuntu. "
    "Keep responses clear and well-structured. Avoid visual formatting that "
    "does not read well as linear text.\n\n"
    "When producing a file (Python, YAML, Bash, SQL, Markdown), always wrap "
    "the entire file content in named markers exactly like this:\n\n"
    "=== BEGIN FILE: path/to/filename.py ===\n"
    "... file content ...\n"
    "=== END FILE: path/to/filename.py ===\n\n"
    "Use the actual relative path from the project root as the filename. "
    "This allows Jan to extract files from saved conversations automatically.\n\n"
    "When producing Python code: use 4-space indentation, include block "
    "markers (# --- function name --- and # --- end function name ---) "
    "around all function definitions, and use .format() instead of f-strings "
    "for Python 3.10 compatibility."
)

COMMANDS = (
    "/quit", "/q", "/clear", "/save", "/history",
    "/sessions", "/file", "/extract"
)

# Tracks the last saved transcript file path for /extract
_last_transcript_file = ""


# ---------------------------------------------------------------------------
# --- log_dir ---------------------------------------------------------------
# ---------------------------------------------------------------------------

def ensure_log_dir() -> Path:
    """
    Ensure the project log directory exists.
    Falls back to current working directory on failure.
    Never exits -- transcript failure must not kill the session.
    """
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        return LOG_DIR
    except OSError as e:
        print(
            "WARNING: Cannot create log dir {}: {}".format(LOG_DIR, e),
            file=sys.stderr
        )
        print("WARNING: Transcripts will be written to current directory.")
        return Path.cwd()

# --- end ensure_log_dir ----------------------------------------------------


# ---------------------------------------------------------------------------
# --- Session persistence ---------------------------------------------------
# ---------------------------------------------------------------------------

def ensure_sessions_dir() -> Path:
    """Ensure ~/.claude_sessions exists. Returns None on failure."""
    try:
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        return SESSIONS_DIR
    except OSError as e:
        print(
            "ERROR: Cannot create sessions directory {}: {}".format(
                SESSIONS_DIR, e),
            file=sys.stderr
        )
        return None

# --- end ensure_sessions_dir -----------------------------------------------


def session_path(name: str) -> Path:
    """Return the full path for a named session JSON file."""
    safe = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
    return SESSIONS_DIR / "{}.json".format(safe)

# --- end session_path ------------------------------------------------------


def load_session(name: str) -> list:
    """
    Load a named session from JSON.
    Returns history list, or empty list if session does not exist.
    """
    path = session_path(name)
    if not path.exists():
        print("Session '{}' not found -- starting fresh.".format(name))
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        history = data.get("history", [])
        saved_at = data.get("saved_at", "unknown")
        turns = len([t for t in history if t.get("role") != "_pending_file"])
        print("Session '{}' loaded: {} turns, last saved {}.".format(
            name, turns, saved_at))
        return history
    except (json.JSONDecodeError, OSError) as e:
        print(
            "ERROR: Cannot load session '{}': {}".format(name, e),
            file=sys.stderr
        )
        return []

# --- end load_session -------------------------------------------------------


def save_session(name: str, history: list) -> bool:
    """
    Save current session to named JSON file in ~/.claude_sessions/
    Returns True on success. Never exits -- session continues on failure.
    """
    if not ensure_sessions_dir():
        return False

    real_history = [t for t in history if t.get("role") != "_pending_file"]
    data = {
        "session_name": name,
        "saved_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "model": MODEL,
        "project_root": str(PROJECT_ROOT),
        "turns": len(real_history),
        "history": real_history
    }

    path = session_path(name)
    try:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        return True
    except (PermissionError, OSError) as e:
        print(
            "ERROR: Cannot save session '{}': {}".format(name, e),
            file=sys.stderr
        )
        print("Session continues -- not saved to disk.")
        return False

# --- end save_session -------------------------------------------------------


def list_sessions() -> None:
    """List all saved sessions with turn counts and save times."""
    if not ensure_sessions_dir():
        return
    files = sorted(SESSIONS_DIR.glob("*.json"))
    if not files:
        print("No saved sessions in {}.".format(SESSIONS_DIR))
        return
    print("Saved sessions in {}:".format(SESSIONS_DIR))
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            print("  {}  ({} turns, saved {})".format(
                data.get("session_name", f.stem),
                data.get("turns", "?"),
                data.get("saved_at", "?")))
        except (json.JSONDecodeError, OSError):
            print("  {} (unreadable)".format(f.stem))

# --- end list_sessions ------------------------------------------------------


# ---------------------------------------------------------------------------
# --- File reading ----------------------------------------------------------
# ---------------------------------------------------------------------------

def read_file(path: str, exit_on_error: bool = False) -> str:
    """
    Read a file and return its contents as a string.
    exit_on_error=True: exit on failure (startup, no session to lose).
    exit_on_error=False: print error, return empty string, session continues.
    """
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        print("ERROR: File not found: {}".format(path), file=sys.stderr)
    except PermissionError:
        print("ERROR: Permission denied: {}".format(path), file=sys.stderr)
    except IsADirectoryError:
        print("ERROR: Path is a directory: {}".format(path), file=sys.stderr)
    except OSError as e:
        print("ERROR: Cannot read {}: {}".format(path, e), file=sys.stderr)

    if exit_on_error:
        sys.exit(1)
    return ""

# --- end read_file ---------------------------------------------------------


# ---------------------------------------------------------------------------
# --- Transcript save -------------------------------------------------------
# ---------------------------------------------------------------------------

def save_transcript(history: list) -> str:
    """
    Save conversation as plain text transcript to the project log/ directory.
    Used by /extract to find file blocks.
    Returns the transcript file path, or empty string on failure.
    Never exits.
    """
    global _last_transcript_file

    real_turns = [t for t in history if t.get("role") != "_pending_file"]
    if not real_turns:
        print("Nothing to save yet -- have a conversation first.")
        return ""

    log_dir = ensure_log_dir()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = log_dir / "transcript_{}.txt".format(timestamp)

    try:
        with open(str(filename), "w", encoding="utf-8") as f:
            for turn in real_turns:
                f.write("=== {} ===\n{}\n\n".format(
                    turn["role"].upper(), turn["content"]))
        print("Transcript: {} ({} turns)".format(filename, len(real_turns)))
        _last_transcript_file = str(filename)
        return str(filename)
    except (PermissionError, OSError) as e:
        print("ERROR: Cannot save transcript: {}".format(e), file=sys.stderr)
        print("Session continues.")
        return ""

# --- end save_transcript ---------------------------------------------------


# ---------------------------------------------------------------------------
# --- File extraction -------------------------------------------------------
# ---------------------------------------------------------------------------

def extract_file(target_path: str, transcript_file: str) -> None:
    """
    Extract a named file block from a saved transcript and write to disk.
    Path is relative to PROJECT_ROOT (where this script lives).
    Prints the absolute path of the written file so you know where it went.
    Never exits.
    """
    if not transcript_file:
        print("No transcript saved yet. Run /save first, then /extract.")
        return

    text = read_file(transcript_file, exit_on_error=False)
    if not text:
        return

    escaped = re.escape(target_path)
    pattern = (
        r"=== BEGIN FILE: " + escaped + r" ===\n"
        r"(.*?)"
        r"=== END FILE: " + escaped + r" ==="
    )
    match = re.search(pattern, text, re.DOTALL)

    if not match:
        print("ERROR: No block found for '{}' in transcript.".format(target_path))
        print("Open the transcript in Vim and search for BEGIN FILE")
        print("to see the exact path Claude used, then retry.")
        print("Transcript: {}".format(transcript_file))
        return

    content = match.group(1)
    if content.startswith("\n"):
        content = content[1:]

    # Write relative to PROJECT_ROOT so it always lands in the right place
    output_path = PROJECT_ROOT / target_path
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        print("Extracted: {}".format(output_path))
        print("Size: {} bytes".format(len(content)))
    except PermissionError:
        print("ERROR: Permission denied: {}".format(output_path), file=sys.stderr)
    except OSError as e:
        print("ERROR: Cannot write {}: {}".format(output_path, e), file=sys.stderr)

# --- end extract_file ------------------------------------------------------


# ---------------------------------------------------------------------------
# --- API call --------------------------------------------------------------
# ---------------------------------------------------------------------------

def send_message(client: anthropic.Anthropic, history: list) -> str:
    """
    Send conversation history to API. Returns response text or empty string.
    Auth failure exits (not recoverable). All other errors return empty string.
    """
    api_history = [t for t in history if t.get("role") != "_pending_file"]

    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=api_history
        )
        return response.content[0].text

    except anthropic.AuthenticationError:
        print(
            "\nERROR: Authentication failed. Check ANTHROPIC_API_KEY and restart.",
            file=sys.stderr
        )
        sys.exit(1)

    except anthropic.RateLimitError:
        print("\nERROR: Rate limit. Wait a moment and try again.", file=sys.stderr)
        return ""

    except anthropic.APIConnectionError:
        print("\nERROR: Cannot connect. Check internet.", file=sys.stderr)
        return ""

    except anthropic.BadRequestError as e:
        print("\nERROR: API rejected request: {}\nTry /clear.".format(e),
              file=sys.stderr)
        return ""

    except anthropic.APIError as e:
        print("\nERROR: API error: {}".format(e), file=sys.stderr)
        return ""

# --- end send_message ------------------------------------------------------


# ---------------------------------------------------------------------------
# --- Command handler -------------------------------------------------------
# ---------------------------------------------------------------------------

def handle_command(
    command: str,
    history: list,
    client: anthropic.Anthropic,
    session_name: str
) -> tuple:
    """
    Handle a slash command. Returns (continue_chat, history).
    All errors caught and reported. Session never killed.
    """
    parts = command.strip().split(None, 1)
    cmd = parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else ""

    # --- /quit or /q
    if cmd in ("/quit", "/q"):
        if session_name:
            save_session(session_name, history)
            print("Session '{}' saved.".format(session_name))
        print("Goodbye.")
        return False, history

    # --- /clear
    if cmd == "/clear":
        label = session_name if session_name else "none"
        print("Conversation cleared. Session name '{}' kept.".format(label))
        return True, []

    # --- /history
    if cmd == "/history":
        real = sum(1 for t in history if t.get("role") != "_pending_file")
        print("Turns: {}. Session: '{}'.".format(
            real, session_name if session_name else "anonymous"))
        return True, history

    # --- /save
    if cmd == "/save":
        if session_name:
            saved = save_session(session_name, history)
            if saved:
                print("Session '{}' saved to {}.".format(
                    session_name, session_path(session_name)))
        save_transcript(history)
        return True, history

    # --- /sessions
    if cmd == "/sessions":
        list_sessions()
        return True, history

    # --- /file
    if cmd == "/file":
        if not arg:
            print("Usage: /file <path>")
            return True, history
        content = read_file(arg, exit_on_error=False)
        if not content:
            print("File not loaded. Session continues.")
            return True, history
        print("Loaded: {} ({} chars).".format(arg, len(content)))
        print("Type your question and press Enter.")
        if history and history[-1].get("role") == "_pending_file":
            history = history[:-1]
            print("Note: previous unsent file replaced.")
        history.append({"role": "_pending_file", "content": content, "path": arg})
        return True, history

    # --- /extract
    if cmd == "/extract":
        if not arg:
            print("Usage: /extract <path>")
            print("Files written relative to: {}".format(PROJECT_ROOT))
            return True, history
        if not _last_transcript_file:
            print("No transcript saved yet. Run /save first.")
            return True, history
        extract_file(arg, _last_transcript_file)
        return True, history

    print("Unknown command: {}".format(cmd))
    print("Available: {}".format(", ".join(COMMANDS)))
    return True, history

# --- end handle_command ----------------------------------------------------


# ---------------------------------------------------------------------------
# --- Main chat loop --------------------------------------------------------
# ---------------------------------------------------------------------------

def chat_loop(
    client: anthropic.Anthropic,
    history: list,
    session_name: str
) -> None:
    """Main conversation loop."""
    label = session_name if session_name else "anonymous"
    print("\nClaude API ({}) -- Arachnet [{}]".format(MODEL, label))
    print("Project root: {}".format(PROJECT_ROOT))
    print("Transcripts:  {}".format(LOG_DIR))
    if session_name:
        print("Sessions:     {}".format(SESSIONS_DIR))
        print("Auto-saved after every response and on /quit.")
    print("Commands: /quit  /clear  /save  /history  /sessions  /file <p>  /extract <p>")
    print("=" * 60)

    while True:

        try:
            print("\nYOU:")
            user_input = input().strip()
        except EOFError:
            if session_name:
                save_session(session_name, history)
            print("\nGoodbye.")
            break
        except KeyboardInterrupt:
            print("\nCtrl-C caught. Type /quit to exit and save.")
            continue

        if not user_input:
            continue

        if user_input.startswith("/"):
            try:
                continue_chat, history = handle_command(
                    user_input, history, client, session_name)
            except Exception as e:
                print("ERROR: Unexpected error: {}".format(e), file=sys.stderr)
                continue
            if not continue_chat:
                break
            continue

        # --- Consume pending file
        pending_content = ""
        pending_path = ""
        if (history
                and isinstance(history[-1], dict)
                and history[-1].get("role") == "_pending_file"):
            pending_content = history[-1]["content"]
            pending_path = history[-1].get("path", "file")
            history = history[:-1]

        # --- Build message
        if pending_content:
            message_content = "Contents of {}:\n\n{}\n\n---\n\n{}".format(
                pending_path, pending_content, user_input)
        else:
            message_content = user_input

        history.append({"role": "user", "content": message_content})

        print("\nCLAUDE:")
        print("(sending...)")

        try:
            response = send_message(client, history)
        except Exception as e:
            print("ERROR: Unexpected error: {}".format(e), file=sys.stderr)
            history.pop()
            print("Message not sent. Session continues.")
            continue

        if response:
            print(response)
            history.append({"role": "assistant", "content": response})
            if session_name:
                save_session(session_name, history)
        else:
            history.pop()

# --- end chat_loop ---------------------------------------------------------


# ---------------------------------------------------------------------------
# --- Entry point -----------------------------------------------------------
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Parse arguments, initialise client, start chat loop.
    Startup errors exit cleanly -- no session to preserve.
    """
    parser = argparse.ArgumentParser(
        description="Terminal Claude API chat -- Arachnet project"
    )
    parser.add_argument(
        "--session", "-s",
        help="Named session (loads existing or creates new)",
        metavar="NAME"
    )
    parser.add_argument(
        "--file", "-f",
        help="Load this file as initial context",
        metavar="PATH"
    )
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print(
            "ERROR: ANTHROPIC_API_KEY not set.\n"
            "Add to ~/.bashrc:\n"
            "  export ANTHROPIC_API_KEY=\"sk-ant-...\"\n"
            "Then: source ~/.bashrc",
            file=sys.stderr
        )
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    session_name = args.session or ""
    history = []

    if session_name:
        ensure_sessions_dir()
        history = load_session(session_name)

    if args.file:
        content = read_file(args.file, exit_on_error=True)
        history.append({
            "role": "user",
            "content": "Project context:\n\n{}".format(content)
        })
        print("Loaded: {}".format(args.file))
        print("Sending to Claude...")
        response = send_message(client, history)
        if response:
            history.append({"role": "assistant", "content": response})
            print("\nCLAUDE:")
            print(response)
            if session_name:
                save_session(session_name, history)
        else:
            print("WARNING: No response for initial file. Continuing.")

    chat_loop(client, history, session_name)

# --- end main --------------------------------------------------------------


if __name__ == "__main__":
    main()
