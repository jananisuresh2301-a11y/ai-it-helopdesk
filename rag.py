"""
Lightweight RAG layer over a markdown knowledge base.

Uses TF-IDF + cosine similarity rather than neural embeddings so the whole
project runs offline with no extra API calls or GPU/model downloads. Swap
`KnowledgeBase._vectorize` for an embeddings API if the KB grows large or
needs semantic (not just lexical) matching.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import List

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


@dataclass
class Chunk:
    source: str      # filename the chunk came from
    heading: str      # nearest ## heading
    text: str         # chunk body


def _split_into_chunks(filepath: str) -> List[Chunk]:
    """Split a markdown file into chunks on '## ' headings."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    filename = os.path.basename(filepath)
    # Split on level-2 headings, keeping the heading text.
    parts = re.split(r"\n(?=## )", content)
    chunks: List[Chunk] = []
    for part in parts:
        part = part.strip()
        if not part or part.startswith("# "):
            # top-level title only, skip as its own chunk
            if part.startswith("# ") and "\n" not in part:
                continue
        heading_match = re.match(r"##\s+(.*)", part)
        heading = heading_match.group(1).strip() if heading_match else filename
        if part:
            chunks.append(Chunk(source=filename, heading=heading, text=part))
    return chunks


def _normalize(text: str) -> str:
    """
    Lowercase and collapse hyphens so terms like 'Wi-Fi' / 'wifi' and
    'log-in' / 'login' match each other under TF-IDF's word tokenizer
    (which otherwise splits on hyphens and loses the match).
    """
    text = text.lower()
    text = re.sub(r"(\w)-(\w)", r"\1\2", text)
    return text


class KnowledgeBase:
    """Loads all markdown docs in a directory and answers similarity queries."""

    def __init__(self, kb_dir: str):
        self.kb_dir = kb_dir
        self.chunks: List[Chunk] = []
        for fname in sorted(os.listdir(kb_dir)):
            if fname.endswith(".md"):
                self.chunks.extend(_split_into_chunks(os.path.join(kb_dir, fname)))

        if not self.chunks:
            raise ValueError(f"No markdown chunks found in {kb_dir}")

        self._vectorizer = TfidfVectorizer(stop_words="english", preprocessor=_normalize)
        self._matrix = self._vectorizer.fit_transform([c.text for c in self.chunks])

    # Below this cosine-similarity score, a match is considered too weak to
    # trust as grounding — the agent should say so rather than stretch a
    # loosely related doc to fit.
    LOW_CONFIDENCE_THRESHOLD = 0.12

    def retrieve(self, query: str, top_k: int = 3) -> List[Chunk]:
        """Return the top_k most relevant chunks for a query (no scores)."""
        return [c for c, _ in self.retrieve_scored(query, top_k=top_k)]

    def retrieve_scored(self, query: str, top_k: int = 3) -> List[tuple]:
        """Return up to top_k (Chunk, score) pairs, best first, score > 0 only."""
        query_vec = self._vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._matrix).flatten()
        ranked_idx = scores.argsort()[::-1]

        results = []
        for idx in ranked_idx[:top_k]:
            if scores[idx] > 0:
                results.append((self.chunks[idx], float(scores[idx])))
        return results

    def format_context(self, scored_chunks: List[tuple]) -> str:
        """
        Format (Chunk, score) pairs for the system prompt, flagging low
        confidence so the model doesn't over-trust a weak match.
        """
        if not scored_chunks:
            return (
                "No relevant knowledge base entries found for this query. "
                "Do not fabricate a KB-backed procedure — say so, ask a "
                "clarifying question, or offer general best-practice guidance "
                "clearly labeled as such."
            )
        blocks = []
        for chunk, score in scored_chunks:
            confidence = "LOW CONFIDENCE MATCH — " if score < self.LOW_CONFIDENCE_THRESHOLD else ""
            blocks.append(
                f"[{confidence}Source: {chunk.source} | {chunk.heading} | "
                f"relevance: {score:.2f}]\n{chunk.text}"
            )
        return "\n\n---\n\n".join(blocks)
