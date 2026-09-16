"""
Sanity tests for agent/tools.py. Run directly with: python tests/test_tools.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.tools import (  # noqa: E402
    check_disk_space,
    create_support_ticket,
    execute_tool,
    get_system_info,
)


def test_check_disk_space_returns_expected_keys():
    result = check_disk_space()
    for key in ("total_gb", "used_gb", "free_gb", "percent_free", "low_disk_warning"):
        assert key in result, f"Missing key: {key}"


def test_get_system_info_returns_os():
    result = get_system_info()
    assert "os" in result and result["os"], "Expected a non-empty OS field"


def test_create_support_ticket_returns_id():
    result = create_support_ticket("Test issue", "Full description of the test issue")
    assert result["ticket_id"].startswith("TCK-"), "Expected a TCK- prefixed ticket id"
    assert result["priority"] == "normal", "Expected default priority 'normal'"


def test_execute_tool_dispatches_correctly():
    result = execute_tool("check_disk_space", {})
    assert "percent_free" in result


def test_execute_tool_unknown_tool_returns_error():
    result = execute_tool("not_a_real_tool", {})
    assert "error" in result


if __name__ == "__main__":
    tests = [
        test_check_disk_space_returns_expected_keys,
        test_get_system_info_returns_os,
        test_create_support_ticket_returns_id,
        test_execute_tool_dispatches_correctly,
        test_execute_tool_unknown_tool_returns_error,
    ]
    passed, failed = 0, 0
    for t in tests:
        try:
            t()
            print(f"PASS: {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {t.__name__} — {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)
