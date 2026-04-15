#!/usr/bin/env python3
# claude_chat.py
# Terminal chat interface to Claude API for Arachnet project development.
# Designed for use with screen readers (Orca, VoiceOver).
#
# Place this file in the project root: ~/project_embeddings/claude_chat.py
# Always run with venv active from the project root:
#   cd ~/project_embeddings
#   source venv/bin/activate
#   python claude_chat.py --session arachnet
#
# See docs/claude_chat_howto.md for full usage guide.
#
# Requirements:
#   pip install anthropic
#   export ANTHROPIC_API_KEY="sk-ant-..."  # in ~/.bashrc
#
# Usage:
#   python claude_chat.py                              # anonymous, Sonnet
#   python claude_chat.py --session NAME               # named session
#   python claude_chat.py --session NAME --model opus  # use Opus model
#   python claude_chat.py --session NAME --file PATH   # load file as context
#
# Commands:
#   /quit or /q       -- save JSON + transcript, exit
#   /clear            -- clear conversation history
#   /json             -- save session JSON only (mid-session checkpoint)
#   /save             -- save transcript only (use before /extract)
#   /save --last N    -- save last N turns to transcript
#   /history          -- show turn count, session name, model
#   /sessions         -- list all saved sessions
#   /file <path>      -- load file into next message
#   /extract <path>   -- extract file block from last transcript
#                        writes to PROJECT_ROOT/path
#
# Last modified: 2026-04-11

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

MODELS = {
    "sonnet": "claude-sonnet-4-6",
    "opus":   "claude-opus-4-6",
}
DEFAULT_MODEL = "sonnet"
MAX_TOKENS = 8192

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
    "This allows Jan to extract files from saved conversations.\n\n"
    "When producing Python code: use 4-space indentation, include block "
    "markers (# --- function name --- and # --- end function name ---) "
    "around all function definitions, and use .format() not f-strings.\n\n"
    "If a file is too long for one response, end with the comment "
    "# CONTINUES IN NEXT RESPONSE inside the file content (before the "
    "END FILE marker). Keep END FILE closed until the file is complete. "
    "In the next response open a new BEGIN FILE marker and continue."
)

COMMANDS = (
    "/quit", "/q", "/clear", "/json", "/save",
    "/history", "/sessions", "/file", "/extract"
)

_last_transcript_file = ""


# ---------------------------------------------------------------------------
# --- ensure_log_dir --------------------------------------------------------
# ---------------------------------------------------------------------------

def ensure_log_dir() -> Path:
    """Ensure project log/ directory exists. Falls back to cwd on failure."""
    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        return LOG_DIR
    except OSError as e:
        print("WARNING: Cannot create log dir {}: {}".format(LOG_DIR, e),
              file=sys.stderr)
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
        print("ERROR: Cannot create sessions dir {}: {}".format(
            SESSIONS_DIR, e), file=sys.stderr)
        return None

# --- end ensure_sessions_dir -----------------------------------------------


def session_path(name: str) -> Path:
    """Return full path for a named session JSON file."""
    safe = re.sub(r"[^a-zA-Z0-9._-]", "_", name)
    return SESSIONS_DIR / "{}.json".format(safe)

# --- end session_path ------------------------------------------------------


def load_session(name: str) -> list:
    """Load named session from JSON. Returns history list or empty list."""
    path = session_path(name)
    if not path.exists():
        print("Session '{}' not found -- starting fresh.".format(name))
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        history = data.get("history", [])
        saved_at = data.get("saved_at", "unknown")
        model = data.get("model", "unknown")
        turns = len([t for t in history if t.get("role") != "_pending_file"])
        print("Session '{}' loaded: {} turns, model {}, saved {}.".format(
            name, turns, model, saved_at))
        return history
    except (json.JSONDecodeError, OSError) as e:
        print("ERROR: Cannot load session '{}': {}".format(name, e),
              file=sys.stderr)
        return []

# --- end load_session -------------------------------------------------------


def save_session_json(name: str, history: list, model: str) -> bool:
    """
    Save full session history to JSON in ~/.claude_sessions/
    Called by /json command and /quit.
    Returns True on success. Never exits.
    """
    if not name:
        print("No session name set. Use --session NAME to enable JSON saving.")
        return False

    if not ensure_sessions_dir():
        return False

    real_history = [t for t in history if t.get("role") != "_pending_file"]
    data = {
        "session_name": name,
        "saved_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "model": model,
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
        print("JSON saved: {} ({} turns)".format(path, len(real_history)))
        return True
    except (PermissionError, OSError) as e:
        print("ERROR: Cannot save session '{}': {}".format(name, e),
              file=sys.stderr)
        print("Session continues -- not saved.")
        return False

# --- end save_session_json -------------------------------------------------


def list_sessions() -> None:
    """List all saved sessions with turn counts and models."""
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
            print("  {}  ({} turns, model {}, saved {})".format(
                data.get("session_name", f.stem),
                data.get("turns", "?"),
                data.get("model", "?"),
                data.get("saved_at", "?")))
        except (json.JSONDecodeError, OSError):
            print("  {} (unreadable)".format(f.stem))

# --- end list_sessions ------------------------------------------------------


# ---------------------------------------------------------------------------
# --- File reading ----------------------------------------------------------
# ---------------------------------------------------------------------------

def read_file(path: str, exit_on_error: bool = False) -> str:
    """
    Read file and return contents as string.
    exit_on_error=True: sys.exit on failure (startup only).
    exit_on_error=False: print error, return empty string (session safe).
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

def save_transcript(history: list, last_n: int = 0) -> str:
    """
    Save conversation as plain text transcript to project log/ directory.
    If last_n > 0, save only the last N real turns.
    Used by /extract to find file blocks.
    Returns transcript file path or empty string on failure.
    Never exits.
    """
    global _last_transcript_file

    real_turns = [t for t in history if t.get("role") != "_pending_file"]

    if not real_turns:
        print("Nothing to save yet -- have a conversation first.")
        return ""

    if last_n > 0:
        real_turns = real_turns[-last_n:]
        label = " (last {} turns)".format(last_n)
    else:
        label = ""

    log_dir = ensure_log_dir()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = log_dir / "transcript_{}.txt".format(timestamp)

    try:
        with open(str(filename), "w", encoding="utf-8") as f:
            for turn in real_turns:
                f.write("=== {} ===\n{}\n\n".format(
                    turn["role"].upper(), turn["content"]))
        print("Transcript{}: {} ({} turns)".format(
            label, filename, len(real_turns)))
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
    Extract named file block from transcript and write to disk.
    Path is always relative to PROJECT_ROOT regardless of working directory.
    Prints absolute path of written file so you know exactly where it went.
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
        print("ERROR: No block found for '{}' in transcript.".format(
            target_path))
        print("Open the transcript in Vim and search for BEGIN FILE")
        print("to see the exact path Claude used, then retry.")
        print("Transcript: {}".format(transcript_file))
        return

    content = match.group(1)
    if content.startswith("\n"):
        content = content[1:]

    output_path = PROJECT_ROOT / target_path
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        print("Extracted: {}".format(output_path))
        print("Size: {} bytes".format(len(content)))
    except PermissionError:
        print("ERROR: Permission denied: {}".format(output_path),
              file=sys.stderr)
    except OSError as e:
        print("ERROR: Cannot write {}: {}".format(output_path, e),
              file=sys.stderr)

# --- end extract_file ------------------------------------------------------


# ---------------------------------------------------------------------------
# --- API call --------------------------------------------------------------
# ---------------------------------------------------------------------------

def send_message(
    client: anthropic.Anthropic,
    history: list,
    model: str
) -> str:
    """
    Send conversation history to API. Returns response text or empty string.
    Authentication failure exits -- not recoverable.
    All other errors return empty string -- session continues.
    """
    api_history = [t for t in history if t.get("role") != "_pending_file"]

    try:
        response = client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=api_history
        )
        return response.content[0].text

    except anthropic.AuthenticationError:
        print(
            "\nERROR: Authentication failed. Check ANTHROPIC_API_KEY.",
            file=sys.stderr)
        sys.exit(1)

    except anthropic.RateLimitError:
        print("\nERROR: Rate limit. Wait a moment and try again.",
              file=sys.stderr)
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
    session_name: str,
    model: str
) -> tuple:
    """
    Handle a slash command entered by the user.
    Returns (continue_chat, history).
    All errors are caught and reported. Session is never killed.
    """
    parts = command.strip().split()
    cmd = parts[0].lower()

    # --- /quit or /q
    if cmd in ("/quit", "/q"):
        if session_name:
            save_session_json(session_name, history, model)
        save_transcript(history)
        print("Goodbye.")
        return False, history

    # --- /clear
    if cmd == "/clear":
        print("Conversation cleared. Session '{}' kept.".format(
            session_name if session_name else "none"))
        return True, []

    # --- /json  (save session JSON only — mid-session checkpoint)
    if cmd == "/json":
        save_session_json(session_name, history, model)
        return True, history

    # --- /save  (save transcript only, with optional --last N)
    if cmd == "/save":
        last_n = 0
        if "--last" in parts:
            idx = parts.index("--last")
            if idx + 1 < len(parts):
                try:
                    last_n = int(parts[idx + 1])
                except ValueError:
                    print("ERROR: --last requires a number. "
                          "Example: /save --last 10")
                    return True, history
            else:
                print("ERROR: --last requires a number. "
                      "Example: /save --last 10")
                return True, history
        save_transcript(history, last_n=last_n)
        return True, history

    # --- /history
    if cmd == "/history":
        real = sum(1 for t in history if t.get("role") != "_pending_file")
        print("Turns: {}. Session: '{}'. Model: {}.".format(
            real,
            session_name if session_name else "anonymous",
            model))
        return True, history

    # --- /sessions
    if cmd == "/sessions":
        list_sessions()
        return True, history

    # --- /file
    if cmd == "/file":
        if len(parts) < 2:
            print("Usage: /file <path>")
            return True, history
        arg = parts[1]
        content = read_file(arg, exit_on_error=False)
        if not content:
            print("File not loaded. Session continues.")
            return True, history
        print("Loaded: {} ({} chars).".format(arg, len(content)))
        print("Type your question and press Enter.")
        if history and history[-1].get("role") == "_pending_file":
            history = history[:-1]
            print("Note: previous unsent file replaced.")
        history.append({
            "role": "_pending_file",
            "content": content,
            "path": arg
        })
        return True, history

    # --- /extract
    if cmd == "/extract":
        if len(parts) < 2:
            print("Usage: /extract <path>")
            print("Writes to: {}/path".format(PROJECT_ROOT))
            return True, history
        arg = parts[1]
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
    session_name: str,
    model: str
) -> None:
    """Main conversation loop."""
    label = session_name if session_name else "anonymous"
    print("\nClaude API -- Arachnet [session: {}] [model: {}]".format(
        label, model))
    print("Project root: {}".format(PROJECT_ROOT))
    print("Transcripts:  {}".format(LOG_DIR))
    if session_name:
        print("Sessions:     {}".format(SESSIONS_DIR))
    print("Commands: /quit  /clear  /json  /save [--last N]  "
          "/history  /sessions  /file <p>  /extract <p>")
    print("See docs/claude_chat_howto.md for full guide.")
    print("=" * 60)

    while True:

        try:
            print("\nYOU:")
            user_input = input().strip()
        except EOFError:
            if session_name:
                save_session_json(session_name, history, model)
            save_transcript(history)
            print("\nGoodbye.")
            break
        except KeyboardInterrupt:
            print("\nCtrl-C caught. Type /quit to save and exit.")
            continue

        if not user_input:
            continue

        if user_input.startswith("/"):
            try:
                continue_chat, history = handle_command(
                    user_input, history, client, session_name, model)
            except Exception as e:
                print("ERROR: Unexpected error in command: {}".format(e),
                      file=sys.stderr)
                continue
            if not continue_chat:
                break
            continue

        # --- Consume pending file if present
        pending_content = ""
        pending_path = ""
        if (history
                and isinstance(history[-1], dict)
                and history[-1].get("role") == "_pending_file"):
            pending_content = history[-1]["content"]
            pending_path = history[-1].get("path", "file")
            history = history[:-1]

        # --- Build message content
        if pending_content:
            message_content = "Contents of {}:\n\n{}\n\n---\n\n{}".format(
                pending_path, pending_content, user_input)
        else:
            message_content = user_input

        history.append({"role": "user", "content": message_content})

        print("\nCLAUDE [{}]:".format(model))
        print("(sending...)")

        try:
            response = send_message(client, history, model)
        except Exception as e:
            print("ERROR: Unexpected error: {}".format(e), file=sys.stderr)
            history.pop()
            print("Message not sent. Session continues.")
            continue

        if response:
            print(response)
            history.append({"role": "assistant", "content": response})
        else:
            history.pop()

# --- end chat_loop ---------------------------------------------------------


# ---------------------------------------------------------------------------
# --- Entry point -----------------------------------------------------------
# ---------------------------------------------------------------------------

def main() -> None:
    """
    Parse arguments, initialise client, start chat loop.
    Startup errors exit cleanly -- no session to preserve yet.
    """
    parser = argparse.ArgumentParser(
        description="Terminal Claude API chat -- Arachnet project"
    )
    parser.add_argument(
        "--session", "-s",
        help="Named session: loads existing or creates new",
        metavar="NAME"
    )
    parser.add_argument(
        "--file", "-f",
        help="Load this file as initial context before chat starts",
        metavar="PATH"
    )
    parser.add_argument(
        "--model", "-m",
        help="Model: sonnet (default, fast) or opus (slower, more capable)",
        choices=list(MODELS.keys()),
        default=DEFAULT_MODEL,
        metavar="MODEL"
    )
    args = parser.parse_args()

    model = MODELS[args.model]

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        print(
            "ERROR: ANTHROPIC_API_KEY not set.\n"
            "Add to ~/.bashrc:\n"
            "  export ANTHROPIC_API_KEY=\"sk-ant-...\"\n"
            "Then: source ~/.bashrc",
            file=sys.stderr)
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
        print("Sending to Claude [{}]...".format(model))
        response = send_message(client, history, model)
        if response:
            history.append({"role": "assistant", "content": response})
            print("\nCLAUDE [{}]:".format(model))
            print(response)
        else:
            print("WARNING: No response for initial file. Continuing.")

    chat_loop(client, history, session_name, model)

# --- end main --------------------------------------------------------------


if __name__ == "__main__":
    main()
