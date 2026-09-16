"""
Diagnostic tools the agent can call.

Each tool is a plain Python function plus a JSON schema entry in TOOLS
(Anthropic tool-use format). All checks here are read-only and safe to run.
`restart_service` is a simulated stub — wire it up to your real RMM /
service-management API before using it against production systems.
"""

from __future__ import annotations

import platform
import shutil
import subprocess
from typing import Any, Dict


def check_network_connectivity(host: str = "8.8.8.8") -> Dict[str, Any]:
    """Ping a host to check basic network connectivity and latency."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        result = subprocess.run(
            ["ping", param, "3", host],
            capture_output=True,
            text=True,
            timeout=10,
        )
        reachable = result.returncode == 0
        return {
            "host": host,
            "reachable": reachable,
            "output": result.stdout[-800:] if result.stdout else result.stderr[-800:],
        }
    except Exception as e:  # noqa: BLE001 - surface any failure to the agent
        return {"host": host, "reachable": False, "error": str(e)}


def check_disk_space() -> Dict[str, Any]:
    """Check free disk space on the system drive."""
    try:
        total, used, free = shutil.disk_usage("/")
        percent_free = round((free / total) * 100, 1)
        return {
            "total_gb": round(total / (1024 ** 3), 1),
            "used_gb": round(used / (1024 ** 3), 1),
            "free_gb": round(free / (1024 ** 3), 1),
            "percent_free": percent_free,
            "low_disk_warning": percent_free < 15,
        }
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


def get_system_info() -> Dict[str, Any]:
    """Return basic OS / hardware info useful for diagnosis."""
    try:
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        }
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


def check_service_status(service_name: str) -> Dict[str, Any]:
    """
    Check whether a named service/process appears to be running.
    Simplified cross-platform process-name lookup (not a full service
    manager query) — good enough for demo/diagnostic purposes.
    """
    try:
        if platform.system().lower() == "windows":
            result = subprocess.run(
                ["sc", "query", service_name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            running = "RUNNING" in result.stdout
            output = result.stdout[-500:]
        else:
            result = subprocess.run(
                ["pgrep", "-f", service_name],
                capture_output=True,
                text=True,
                timeout=10,
            )
            running = bool(result.stdout.strip())
            output = result.stdout[-500:] or "No matching process found."
        return {"service_name": service_name, "running": running, "output": output}
    except Exception as e:  # noqa: BLE001
        return {"service_name": service_name, "error": str(e)}


def create_support_ticket(
    summary: str, description: str, priority: str = "normal"
) -> Dict[str, Any]:
    """
    SIMULATED: Escalate to a human technician by creating a support ticket.
    Replace this stub with a real call to your ticketing system (Jira
    Service Management, ServiceNow, Zendesk, etc.) before production use.
    """
    import time
    import uuid

    ticket_id = f"TCK-{uuid.uuid4().hex[:8].upper()}"
    return {
        "ticket_id": ticket_id,
        "summary": summary,
        "priority": priority,
        "status": "simulated_created",
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "note": (
            "This is a simulated ticket. Wire this function up to your real "
            "ticketing system's API before relying on it in production."
        ),
    }


def restart_service(service_name: str) -> Dict[str, Any]:
    """
    SIMULATED: Restart a named service. Replace this stub with a real call
    to your service manager / RMM API before using in production. Left as a
    simulation here so the agent can be demoed safely without side effects.
    """
    return {
        "service_name": service_name,
        "status": "simulated_restart_success",
        "note": (
            "This is a simulated action. Wire this function up to your real "
            "service-management tooling (e.g. systemctl, Windows SCM, RMM "
            "API) before relying on it in production."
        ),
    }


# --- Anthropic tool-use schema definitions -------------------------------

TOOLS = [
    {
        "name": "check_network_connectivity",
        "description": (
            "Ping a host (default 8.8.8.8) to check whether the machine has "
            "working network connectivity and to gauge latency/packet loss."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "host": {
                    "type": "string",
                    "description": "Hostname or IP to ping. Defaults to 8.8.8.8.",
                }
            },
        },
    },
    {
        "name": "check_disk_space",
        "description": "Check free disk space on the system drive.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_system_info",
        "description": "Get basic OS, version, and hardware info for the machine.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "check_service_status",
        "description": (
            "Check whether a named service or process (e.g. 'spooler', "
            "'sshd') appears to be running."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "Name of the service or process to check.",
                }
            },
            "required": ["service_name"],
        },
    },
    {
        "name": "create_support_ticket",
        "description": (
            "Escalate to a human technician by creating a support ticket "
            "(SIMULATED in this scaffold). Use this when the issue can't be "
            "resolved through the knowledge base or available diagnostics, "
            "or when it requires physical/administrative access you don't have."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "One-line summary of the issue.",
                },
                "description": {
                    "type": "string",
                    "description": (
                        "Full details: symptoms, what's been tried, and any "
                        "diagnostic results gathered so far."
                    ),
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "normal", "high", "urgent"],
                    "description": "Ticket priority. Defaults to 'normal'.",
                },
            },
            "required": ["summary", "description"],
        },
    },
    {
        "name": "restart_service",
        "description": (
            "Restart a named service (SIMULATED in this scaffold — does not "
            "actually restart anything until wired to real infra)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "service_name": {
                    "type": "string",
                    "description": "Name of the service to restart.",
                }
            },
            "required": ["service_name"],
        },
    },
]

_DISPATCH = {
    "check_network_connectivity": check_network_connectivity,
    "check_disk_space": check_disk_space,
    "get_system_info": get_system_info,
    "check_service_status": check_service_status,
    "restart_service": restart_service,
    "create_support_ticket": create_support_ticket,
}


def execute_tool(name: str, tool_input: Dict[str, Any]) -> Dict[str, Any]:
    """Dispatch a tool call by name to its implementation."""
    fn = _DISPATCH.get(name)
    if fn is None:
        return {"error": f"Unknown tool '{name}'"}
    return fn(**tool_input)
