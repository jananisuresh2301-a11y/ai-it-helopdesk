# Changelog

## v1.1.0 — Featured update

### Added
- **Ticket escalation tool** (`create_support_ticket`): the agent can now
  hand off to a human technician (simulated) when the knowledge base and
  diagnostics don't resolve an issue, instead of guessing.
- **Retrieval confidence scoring**: `KnowledgeBase.retrieve_scored()` returns
  similarity scores alongside chunks; weak matches are labeled
  "LOW CONFIDENCE MATCH" in the system prompt so the agent doesn't force a
  fit to an unrelated KB entry.
- **Conversation logging** (`agent/logger.py`): every user message, RAG
  retrieval, tool call, and agent reply is written to a per-session JSONL
  file under `logs/` for QA/audit purposes.
- **Transcript export**: `HelpdeskAgent.export_transcript_markdown()` plus a
  new `save [file]` CLI command to export the current conversation to a
  readable markdown file.
- **Richer CLI**: markdown-formatted agent replies via `rich` (falls back to
  plain text if `rich` isn't installed), plus `help` and `save` commands.
- **Tool tests** (`tests/test_tools.py`) covering disk space, system info,
  ticket creation, and the tool dispatcher.
- **CI**: GitHub Actions workflow (`.github/workflows/tests.yml`) runs the
  test suite on every push/PR to `main`.
- **Docker support**: `Dockerfile` and `.dockerignore` for containerized
  deployment (includes `iputils-ping` so network checks work in-container).
- `LICENSE` (MIT) and `requirements-dev.txt`.

### Changed
- `HelpdeskAgent` now takes `enable_logging` / `log_dir` options.
- System prompt updated to describe the new escalation capability and to
  instruct the model not to over-trust low-confidence KB matches.

## v1.0.0 — Initial release
- Agent loop combining Claude (Anthropic API), TF-IDF RAG over a markdown
  knowledge base, and read-only diagnostic tools (network, disk, service
  status, system info, simulated service restart).
- CLI entry point, knowledge base covering Wi-Fi/slow computer/printer/
  password/email/VPN issues, and RAG retrieval tests.
