"""
Agent orchestration: combines RAG retrieval with tool-calling in a loop
around the Claude Messages API.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List

from .llm_client import LLMClient
from .logger import ConversationLogger
from .rag import KnowledgeBase
from .tools import TOOLS, execute_tool

SYSTEM_PROMPT_TEMPLATE = """\
You are an AI IT helpdesk agent. You diagnose common technical issues and \
recommend concrete troubleshooting steps.

You have three capabilities:
1. Knowledge base context (retrieved below) — documented procedures for \
common issues. Ground your diagnosis in this when it's relevant. Matches \
labeled LOW CONFIDENCE MATCH may not actually apply — don't force a fit.
2. Diagnostic tools — read-only checks (network, disk, service status, \
system info) you can run on the user's machine to confirm hypotheses \
before recommending fixes. Use them when they would help confirm a \
diagnosis rather than guessing.
3. Escalation — if the knowledge base has no relevant procedure, the \
diagnostics don't resolve it, or the fix needs access/permissions you \
don't have, use create_support_ticket to hand it to a human technician \
rather than guessing at an unsupported fix.

Guidelines:
- Ask a clarifying question only if the issue is too vague to act on.
- Prefer running a relevant diagnostic tool over asking the user to run \
commands themselves, when a tool is available for it.
- Base your recommendations on the knowledge base context when it applies; \
say so if you're going beyond it, and say so if no good match was found.
- Give a short diagnosis, then a numbered list of concrete next steps.
- Do not take destructive actions (e.g. restarting a service) without \
first explaining what you're about to do.
- When you escalate, tell the user the ticket ID and a one-line reason.

Relevant knowledge base context for this user turn:
{kb_context}
"""


class HelpdeskAgent:
    def __init__(
        self,
        kb_dir: str = "knowledge_base",
        top_k: int | None = None,
        enable_logging: bool = True,
        log_dir: str = "logs",
    ):
        self.kb = KnowledgeBase(kb_dir)
        self.llm = LLMClient()
        self.top_k = top_k or int(os.environ.get("RAG_TOP_K", 3))
        self.max_steps = int(os.environ.get("MAX_AGENT_STEPS", 6))
        self.history: List[Dict[str, Any]] = []
        self.logger = ConversationLogger(log_dir) if enable_logging else None

    def _build_system_prompt(self, user_message: str) -> str:
        scored_chunks = self.kb.retrieve_scored(user_message, top_k=self.top_k)
        kb_context = self.kb.format_context(scored_chunks)
        if self.logger:
            self.logger.log(
                "rag_retrieval",
                {
                    "query": user_message,
                    "matches": [
                        {"source": c.source, "heading": c.heading, "score": round(s, 3)}
                        for c, s in scored_chunks
                    ],
                },
            )
        return SYSTEM_PROMPT_TEMPLATE.format(kb_context=kb_context)

    def handle_message(self, user_message: str) -> str:
        system_prompt = self._build_system_prompt(user_message)
        self.history.append({"role": "user", "content": user_message})
        if self.logger:
            self.logger.log("user_message", {"content": user_message})

        for _ in range(self.max_steps):
            response = self.llm.create_message(
                system=system_prompt,
                messages=self.history,
                tools=TOOLS,
            )

            # Collect assistant content blocks for history.
            assistant_content = [block.model_dump() for block in response.content]
            self.history.append({"role": "assistant", "content": assistant_content})

            if response.stop_reason != "tool_use":
                # Final answer — concatenate any text blocks.
                text = "".join(
                    block.text for block in response.content if block.type == "text"
                )
                if self.logger:
                    self.logger.log("agent_reply", {"content": text})
                return text

            # Execute every requested tool call and feed results back.
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    if self.logger:
                        self.logger.log(
                            "tool_call",
                            {"name": block.name, "input": block.input, "result": result},
                        )
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result),
                        }
                    )
            self.history.append({"role": "user", "content": tool_results})

        return (
            "I wasn't able to reach a final answer within the allotted "
            "diagnostic steps. Here's what I found so far — let me know if "
            "you'd like me to keep going."
        )

    def reset(self):
        self.history = []
        if self.logger:
            self.logger = ConversationLogger(self.logger.log_dir)

    def export_transcript_markdown(self) -> str:
        """Render the current conversation history as a readable markdown transcript."""
        lines = ["# Conversation Transcript\n"]
        for msg in self.history:
            role = msg["role"]
            content = msg["content"]
            if isinstance(content, str):
                lines.append(f"**{role.capitalize()}:** {content}\n")
                continue
            for block in content:
                btype = block.get("type")
                if btype == "text":
                    lines.append(f"**{role.capitalize()}:** {block['text']}\n")
                elif btype == "tool_use":
                    lines.append(
                        f"*Tool call → {block['name']}({block.get('input', {})})*\n"
                    )
                elif btype == "tool_result":
                    lines.append(f"*Tool result: {block.get('content')}*\n")
        return "\n".join(lines)
