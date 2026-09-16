# AI IT Helpdesk Agent

An AI-powered IT helpdesk agent that diagnoses common technical issues and
recommends troubleshooting steps. It combines three capabilities:

- **Agent** — an LLM-driven control loop (Claude via the Anthropic API) that
  decides what to do next: search the knowledge base, run a diagnostic tool,
  or answer the user.
- **RAG** — a lightweight retrieval layer (TF-IDF + cosine similarity) over a
  markdown knowledge base of common IT issues, so answers are grounded in
  your documented procedures instead of guesswork.
- **Tools** — function-calling "hands" the agent can use to actually inspect
  the machine it's running on: network connectivity, disk space, service
  status, system info, and escalation to a human via a support ticket.

## What's new in v1.1

- **Escalation**: a `create_support_ticket` tool so the agent hands off to a
  human instead of guessing when the KB/diagnostics come up short.
- **Confidence-aware retrieval**: weak KB matches are flagged so the agent
  doesn't force-fit an unrelated procedure.
- **Conversation logging**: JSONL session logs under `logs/` for QA/audit.
- **Transcript export**: `save [file]` CLI command, backed by
  `HelpdeskAgent.export_transcript_markdown()`.
- **Richer CLI** (via `rich`), tool tests, CI (GitHub Actions), Docker
  support, MIT license. See `CHANGELOG.md` for full details.

## Architecture

```
                     ┌─────────────────────┐
   user message ───▶ │      Agent Loop      │
                     │   (agent/agent.py)   │
                     └──────────┬───────────┘
                                │
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                 ▼
     ┌────────────────┐ ┌───────────────┐ ┌────────────────┐
     │  RAG retrieval  │ │  Claude (LLM)  │ │  Tool execution │
     │  (agent/rag.py) │ │ (llm_client.py)│ │ (agent/tools.py)│
     └────────┬────────┘ └───────┬────────┘ └────────┬────────┘
              │                                       │
     ┌────────▼────────┐                    ┌─────────▼─────────┐
     │ knowledge_base/  │                    │ ping / disk / svc │
     │   *.md docs      │                    │ checks on host OS │
     └──────────────────┘                    └────────────────────┘
```

Flow for each user turn:
1. The user's message is embedded (TF-IDF) and matched against chunks of the
   markdown knowledge base; the top matches are injected into the system
   prompt as grounding context.
2. Claude is called with that context plus a set of tool definitions
   (`agent/tools.py`).
3. If Claude requests a tool (e.g. "check network connectivity"), the agent
   executes it locally and feeds the result back to Claude.
4. Claude repeats step 3 as needed, then produces a final diagnosis and
   recommended troubleshooting steps.

## Project layout

```
ai-it-helpdesk-agent/
├── README.md
├── CHANGELOG.md
├── LICENSE
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
├── .dockerignore
├── Dockerfile
├── main.py                  # CLI entry point
├── .github/workflows/
│   └── tests.yml             # CI: runs tests on push/PR
├── agent/
│   ├── __init__.py
│   ├── agent.py              # orchestration / agent loop
│   ├── rag.py                # knowledge base + scored retrieval
│   ├── tools.py               # diagnostic + escalation tools & schemas
│   ├── llm_client.py          # Anthropic API wrapper
│   └── logger.py              # JSONL conversation/session logging
├── knowledge_base/
│   ├── wifi_issues.md
│   ├── slow_computer.md
│   ├── printer_issues.md
│   ├── password_reset.md
│   ├── email_issues.md
│   └── vpn_issues.md
└── tests/
    ├── test_rag.py
    └── test_tools.py
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit .env and add your key
```

`.env`:
```
ANTHROPIC_API_KEY=your_api_key_here
# Optional overrides
CLAUDE_MODEL=claude-sonnet-4-6
RAG_TOP_K=3
```

## Run

```bash
python main.py
```

Example session:
```
IT Helpdesk Agent — type 'exit' to quit
You: my laptop wifi keeps disconnecting every few minutes
Agent: [retrieves wifi_issues.md, runs check_network_connectivity]
       It looks like your connection is dropping intermittently...
       1. Update your wifi adapter driver
       2. Forget and reconnect to the network
       3. Check for interference from nearby 5GHz devices
       ...
```

## Extending

- **Add knowledge**: drop a new `.md` file into `knowledge_base/`. Use `##`
  headers to separate topics — the RAG layer chunks on headers.
- **Add a tool**: define a Python function in `agent/tools.py`, add its JSON
  schema to the `TOOLS` list, and register it in `execute_tool()`.
- **Swap the LLM**: `agent/llm_client.py` is the only file that talks to the
  Anthropic API — swap it out to use a different provider if needed.
- **Swap retrieval**: `agent/rag.py` uses TF-IDF for zero-dependency, fast,
  offline retrieval. Swap in embeddings (e.g. `sentence-transformers` or the
  Anthropic/OpenAI embeddings API) for semantic search if your KB grows large.

## Notes

- The diagnostic tools in `agent/tools.py` are safe, read-only checks (ping,
  disk usage, process/service lookups) — no destructive actions are taken
  without being explicit simulated stubs (`restart_service`) you should wire
  up to your real infra (e.g. RMM tooling, ServiceNow, etc.) before production
  use.
- This is a scaffold meant to be adapted to your environment, not a
  drop-in production helpdesk.
