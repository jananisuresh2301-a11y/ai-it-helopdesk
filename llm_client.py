"""Thin wrapper around the Anthropic Messages API."""

from __future__ import annotations

import os
from typing import Any, Dict, List

import anthropic

DEFAULT_MODEL = os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6")


class LLMClient:
    def __init__(self, model: str = DEFAULT_MODEL):
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and "
                "add your key."
            )
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def create_message(
        self,
        system: str,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]] | None = None,
        max_tokens: int = 1024,
    ):
        kwargs: Dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools
        return self.client.messages.create(**kwargs)
