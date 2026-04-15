# claude_chat.py — How-To Guide
## Arachnet Clinical Embeddings

**Document version:** 1.0
**Date:** 2026-04-11
**Script location:** `~/project_embeddings/claude_chat.py`

---

## What this script does

Terminal chat interface to the Claude API. Designed for screen reader
use (Orca on Ubuntu). Maintains conversation history across sessions.
Allows sending project files to Claude and extracting files Claude
produces directly into the project directory structure.

---

## Prerequisites

### One-time setup

Install the anthropic package in the project venv:
```bash
cd ~/project_embeddings
source venv/bin/activate
pip install anthropic
```

Add your API key to `~/.bashrc`:
```bash
export ANTHROPIC_API_KEY="sk-ant-your-key-here"
```

Apply immediately:
```bash
source ~/.bashrc
```

### Every session

Always run from the project root with venv active:
```bash
cd ~/project_embeddings
source venv/bin/activate
python claude_chat.py --session arachnet
```

Or use the alias if configured in `~/.bashrc`:
```bash
claude --session arachnet
```

---

## Starting a session

### New topic — load project summary for context
```bash
python claude_chat.py --session arachnet --file docs/project_summary.md
```
Claude reads the summary and confirms context. Use this at the start
of a new working topic or after a long gap between sessions.

### Continue yesterday's session on the same topic
```bash
python claude_chat.py --session arachnet
```
The full conversation history is loaded from JSON. No need to resend
the summary — Claude already has all previous context.

### Use Opus model for complex problems
```bash
python claude_chat.py --session arachnet --model opus
```
Opus is slower and costs more but handles harder reasoning better.
Use for: complex architectural decisions, subtle bugs Sonnet cannot
resolve, Phase 3 embedding strategy. Use Sonnet for everything else.

### Anonymous session (no history saved)
```bash
python claude_chat.py
```
Nothing is saved to disk. Use for quick throwaway questions.

---

## Commands during chat

### Saving

| Command | What it does | When to use |
|---------|-------------|-------------|
| `/json` | Save session JSON to `~/.claude_sessions/` | Mid-session checkpoint |
| `/save` | Save full transcript to `log/` | Before `/extract` |
| `/save --last N` | Save last N turns to `log/` | When Claude just produced a file |
| `/quit` | Save JSON + transcript, then exit | End of every session |

**Important distinction:**
- JSON (`/json`) saves conversation history for resuming later
- Transcript (`/save`) saves plain text for file extraction
- They are independent — you need both for different purposes

### File workflow

```
/file src/common/config_loader.py
```
Loads the file content. Then type your question and press Enter.
The file content is sent with your question as one message.

```
/save --last 5
```
Saves the last 5 turns as a transcript. Use after Claude produces
a file — you only need the recent turns for extraction.

```
/extract src/common/config_loader.py
```
Finds the file block in the last transcript and writes it to
`PROJECT_ROOT/src/common/config_loader.py`. Overwrites existing file
without warning — commit your work to Git before extracting.

### Other commands

| Command | What it does |
|---------|-------------|
| `/clear` | Clear conversation history (session name kept) |
| `/history` | Show turn count, session name, model |
| `/sessions` | List all saved sessions with details |

### Exiting

`/quit` — saves JSON and transcript, exits cleanly.
`Ctrl-D` — same as /quit, saves and exits.
`Ctrl-C` — does NOT exit. Prints a reminder and continues. Use /quit.

---

## Extracting files Claude produces

Tell Claude explicitly to use file markers:

```
Please write config_loader.py. Use the file markers:
=== BEGIN FILE: src/common/config_loader.py ===
... content ...
=== END FILE: src/common/config_loader.py ===
```

After Claude responds:

```
/save --last 3
/extract src/common/config_loader.py
```

The file is written to `~/project_embeddings/src/common/config_loader.py`.

**If /extract says "No block found":**
Open the transcript in Vim and search for BEGIN FILE to see the exact
path Claude used. Use that exact path in /extract.

```bash
vim log/transcript_2026-04-11_14-23-01.txt
```
Then in Vim: `/BEGIN FILE` and press Enter.

**If Claude splits a long file across responses:**
Claude will end the first response with `# CONTINUES IN NEXT RESPONSE`
inside the file content. Say "continue" and Claude will produce the
rest. Only `/save` after you see the `END FILE` marker.

---

## Session management

Sessions are stored in `~/.claude_sessions/` as JSON files.
Each file contains the complete conversation history.

List all sessions:
```
/sessions
```

Sessions are portable — copy the JSON file to another machine and
load it there:
```bash
scp ~/.claude_sessions/arachnet.json user@other-machine:~/.claude_sessions/
```

Then on the other machine:
```bash
python claude_chat.py --session arachnet
```

---

## End of session workflow

```
/json
/quit
```

Then on the terminal:
```bash
git add .
git commit -m "chore: end of session YYYY-MM-DD"
git push
```

---

## Start of session workflow

```bash
cd ~/project_embeddings
git pull
source venv/bin/activate
python claude_chat.py --session arachnet
```

If starting a new topic:
```bash
python claude_chat.py --session arachnet --file docs/project_summary.md
```

---

## Token costs and efficiency

Every message sends the full conversation history to the API.
Longer sessions cost more per message as history grows.

**To keep costs low:**
- Start a new session when moving to a new topic
- Use `/save --last N` not `/save` when only extracting a recent file
- Use Sonnet (default) for most work, Opus only when needed
- Sonnet: $3/$15 per million input/output tokens
- Opus: $5/$25 per million input/output tokens
- A typical 20-turn development session costs $0.10 to $0.20 total

---

## Troubleshooting

**"ANTHROPIC_API_KEY not set"**
Run `echo $ANTHROPIC_API_KEY`. If empty, check `~/.bashrc` and run
`source ~/.bashrc`.

**"Authentication failed"**
Your API key is wrong or revoked. Get a new key from
console.anthropic.com and update `~/.bashrc`.

**"Rate limit"**
Wait 30 seconds and try again. You have not run out of credits —
you have exceeded the requests-per-minute limit.

**"File not found" on /file**
Check the path. Paths are relative to where you ran the script,
not the project root. Always run from `~/project_embeddings/`.

**"No block found" on /extract**
Claude used a slightly different path in the BEGIN FILE marker.
Open the transcript in Vim, search for BEGIN FILE, use the exact
path shown.

**Session loads but history seems wrong**
Run `/history` to see turn count. If too long, run `/clear` to
start fresh while keeping the session name, then send the project
summary:
```
/clear
```
Then restart with `--file docs/project_summary.md`.

---

## File locations

| What | Where |
|------|-------|
| Script | `~/project_embeddings/claude_chat.py` |
| Session JSON files | `~/.claude_sessions/NAME.json` |
| Transcripts | `~/project_embeddings/log/transcript_*.txt` |
| Extracted files | `~/project_embeddings/PATH` (as specified in /extract) |
| This guide | `~/project_embeddings/docs/claude_chat_howto.md` |

---

## Attribution

This material includes SNOMED Clinical Terms (SNOMED CT) which is used
by permission of SNOMED International. SNOMED and SNOMED CT are
registered trademarks of SNOMED International.
