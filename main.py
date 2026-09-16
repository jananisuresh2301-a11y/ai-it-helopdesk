#!/usr/bin/env python3
"""CLI entry point for the AI IT Helpdesk Agent."""

import os
import sys

from dotenv import load_dotenv

load_dotenv()

from agent.agent import HelpdeskAgent  # noqa: E402

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    _console = Console()
except ImportError:  # rich is optional at runtime; fall back to plain prints
    _console = None

HELP_TEXT = """\
Commands:
  exit / quit   End the session
  reset         Clear conversation history and start fresh
  save [file]   Export the transcript so far to a markdown file
                (default: transcript.md)
  help          Show this message
"""


def _print_agent_reply(reply: str):
    if _console:
        _console.print(Panel(Markdown(reply), title="Agent", border_style="cyan"))
    else:
        print(f"\nAgent: {reply}\n")


def _print(text: str):
    if _console:
        _console.print(text)
    else:
        print(text)


def main():
    try:
        agent = HelpdeskAgent(kb_dir=os.path.join(os.path.dirname(__file__), "knowledge_base"))
    except RuntimeError as e:
        print(f"Setup error: {e}")
        sys.exit(1)

    _print("[bold cyan]IT Helpdesk Agent[/bold cyan] — describe your issue "
           "(type 'help' for commands)\n" if _console else
           "IT Helpdesk Agent — describe your issue (type 'help' for commands)\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_input:
            continue

        lowered = user_input.lower()
        if lowered in {"exit", "quit"}:
            print("Goodbye.")
            break
        if lowered == "help":
            _print(HELP_TEXT)
            continue
        if lowered == "reset":
            agent.reset()
            _print("(conversation reset)\n")
            continue
        if lowered.startswith("save"):
            parts = user_input.split(maxsplit=1)
            filename = parts[1] if len(parts) > 1 else "transcript.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(agent.export_transcript_markdown())
            _print(f"(transcript saved to {filename})\n")
            continue

        try:
            reply = agent.handle_message(user_input)
        except Exception as e:  # noqa: BLE001
            _print(f"Error: {e}\n")
            continue

        _print_agent_reply(reply)


if __name__ == "__main__":
    main()
