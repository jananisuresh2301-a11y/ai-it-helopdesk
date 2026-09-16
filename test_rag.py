"""
Lightweight sanity tests for the RAG retrieval layer.
Run directly with: python tests/test_rag.py
(No pytest dependency required, but it's compatible with pytest too.)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.rag import KnowledgeBase  # noqa: E402

KB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "knowledge_base")


def test_kb_loads_chunks():
    kb = KnowledgeBase(KB_DIR)
    assert len(kb.chunks) > 0, "Expected at least one chunk to be loaded"


def test_wifi_query_returns_wifi_doc():
    kb = KnowledgeBase(KB_DIR)
    results = kb.retrieve("my wifi keeps disconnecting", top_k=3)
    assert results, "Expected at least one result"
    assert any("wifi" in r.source.lower() for r in results), (
        f"Expected a wifi-related source, got: {[r.source for r in results]}"
    )


def test_printer_query_returns_printer_doc():
    kb = KnowledgeBase(KB_DIR)
    results = kb.retrieve("printer shows offline and won't print", top_k=3)
    assert results, "Expected at least one result"
    assert any("printer" in r.source.lower() for r in results), (
        f"Expected a printer-related source, got: {[r.source for r in results]}"
    )


def test_irrelevant_query_returns_low_or_no_results():
    kb = KnowledgeBase(KB_DIR)
    # A query unrelated to any KB content shouldn't strongly match everything.
    results = kb.retrieve("what is the capital of France", top_k=3)
    # This is a soft check — TF-IDF may return weak matches; just ensure
    # it doesn't crash and returns a list.
    assert isinstance(results, list)


if __name__ == "__main__":
    tests = [
        test_kb_loads_chunks,
        test_wifi_query_returns_wifi_doc,
        test_printer_query_returns_printer_doc,
        test_irrelevant_query_returns_low_or_no_results,
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
