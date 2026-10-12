"""Tiny dependency-free RAG: chunk markdown -> TF-IDF vectors -> cosine search."""
import math
import re
from collections import Counter
from functools import lru_cache
from pathlib import Path

KNOWLEDGE_DIR = Path(__file__).resolve().parents[3] / "knowledge"
STOP = set("the a an and or of to in is are for on with that this it as be at by from if than then when".split())


def tokenize(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOP and len(w) > 1]


def chunk_markdown(name: str, text: str) -> list[dict]:
    """Split on '## ' headings so each chunk is one topic."""
    title = text.splitlines()[0].lstrip("# ").strip() if text else name
    chunks = []
    for part in re.split(r"\n(?=## )", text):
        part = part.strip()
        if len(part) > 40:
            chunks.append({"source": name, "title": title, "text": part})
    return chunks


class Index:
    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        docs = [Counter(tokenize(c["title"] + " " + c["text"])) for c in chunks]
        df = Counter(t for d in docs for t in d)
        n = max(len(docs), 1)
        self.idf = {t: math.log((1 + n) / (1 + c)) + 1 for t, c in df.items()}
        self.vecs = [self._vec(d) for d in docs]

    def _vec(self, counts: Counter) -> dict:
        v = {t: c * self.idf.get(t, 0) for t, c in counts.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        return {t: x / norm for t, x in v.items()}

    def search(self, query: str, k: int = 2, min_score: float = 0.05) -> list[dict]:
        q = self._vec(Counter(tokenize(query)))
        scored = [(sum(w * v.get(t, 0) for t, w in q.items()), c) for v, c in zip(self.vecs, self.chunks)]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [{**c, "score": round(s, 3)} for s, c in scored[:k] if s >= min_score]


@lru_cache(maxsize=1)
def get_index() -> Index:
    chunks = []
    for f in sorted(KNOWLEDGE_DIR.glob("*.md")):
        chunks += chunk_markdown(f.name, f.read_text(encoding="utf-8"))
    return Index(chunks)


def search_knowledge(query: str, k: int = 2) -> list[dict]:
    return get_index().search(query, k)
