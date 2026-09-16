"""
Simple JSONL conversation logger for QA/audit purposes.

Each session gets its own file under logs/, one JSON object per line, so
transcripts (including tool calls and their results) can be reviewed later
or fed into eval pipelines.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from typing import Any, Dict


class ConversationLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.session_id = time.strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
        self.path = os.path.join(log_dir, f"session-{self.session_id}.jsonl")

    def log(self, event_type: str, payload: Dict[str, Any]) -> None:
        record = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "event": event_type,
            **payload,
        }
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, default=str) + "\n")
