import re
import numpy as np
from typing import List, Dict

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    _SEMANTIC_AVAILABLE = True
except ImportError:
    _SEMANTIC_AVAILABLE = False


class RAGEngine:
    """
    Semantic RAG engine using sentence-transformers + FAISS.

    Responsibilities:
    - Chunk scraped content into ~300-token segments with 50-token overlap
    - Embed all chunks using SentenceTransformer (all-MiniLM-L6-v2)
    - Build a FAISS IndexFlatL2 index over the embeddings
    - On query: embed the query, retrieve top-k=5 most similar chunks
    - Associate each chunk with nearby hyperlinks from the links list
    - Return grounded answers with clickable sources
    """

    MODEL_NAME = "all-MiniLM-L6-v2"
    CHUNK_SIZE = 300       # target tokens per chunk
    CHUNK_OVERLAP = 50     # overlap tokens between consecutive chunks

    def __init__(self, content: str, links: List[Dict]):
        self.content = content
        self.links = links

        # Tokenize full content once (whitespace tokens)
        self._all_tokens = self.content.split()

        # Build chunks
        self.chunks = self._build_chunks()

        # Build FAISS index
        if _SEMANTIC_AVAILABLE and self.chunks:
            self._model = SentenceTransformer(self.MODEL_NAME)
            self._build_index()
        else:
            self._model = None
            self._index = None
            self._embeddings = None

    # =========================
    # Chunking (~300 tokens, 50-token overlap)
    # =========================
    def _build_chunks(self) -> List[Dict]:
        """
        Create text chunks of ~300 tokens with 50-token overlap.
        Each chunk is associated with nearby hyperlinks.
        """
        tokens = self._all_tokens
        if not tokens:
            return []

        chunks = []
        start = 0

        while start < len(tokens):
            end = min(start + self.CHUNK_SIZE, len(tokens))
            chunk_tokens = tokens[start:end]
            chunk_text = " ".join(chunk_tokens)

            # Calculate character offset range for link proximity matching
            char_start = len(" ".join(tokens[:start])) + (1 if start > 0 else 0)
            char_end = char_start + len(chunk_text)

            matched_links = self._match_links_to_chunk(chunk_text, char_start, char_end)

            chunks.append({
                "text": chunk_text,
                "links": matched_links,
                "token_start": start,
                "token_end": end,
            })

            # Advance by (CHUNK_SIZE - OVERLAP)
            step = self.CHUNK_SIZE - self.CHUNK_OVERLAP
            if start + step >= len(tokens) and end >= len(tokens):
                break
            start += step

        return chunks

    def _match_links_to_chunk(self, chunk_text: str, char_start: int, char_end: int) -> List[Dict]:
        """
        Associate hyperlinks with a chunk by checking whether the link text
        appears in the chunk OR falls within the character-offset proximity
        window in the original content.
        """
        matched = []
        chunk_lower = chunk_text.lower()

        for link in self.links:
            link_text = link.get("text", "").lower()
            if not link_text:
                continue

            # Direct text match: link anchor text appears inside this chunk
            if link_text in chunk_lower:
                matched.append(link)
                continue

            # Proximity match: link anchor appears near this offset range in
            # the full content (within 500 chars of the chunk boundaries)
            pos = self.content.lower().find(link_text)
            if pos != -1:
                margin = 500
                if (char_start - margin) <= pos <= (char_end + margin):
                    matched.append(link)

        return matched

    # =========================
    # FAISS Index
    # =========================
    def _build_index(self):
        """
        Embed all chunks and build a FAISS IndexFlatL2 index.
        """
        texts = [c["text"] for c in self.chunks]
        self._embeddings = self._model.encode(texts, show_progress_bar=False)
        self._embeddings = np.array(self._embeddings, dtype="float32")

        dim = self._embeddings.shape[1]
        self._index = faiss.IndexFlatL2(dim)
        self._index.add(self._embeddings)

    # =========================
    # Retrieval
    # =========================
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Embed the query and retrieve top-k most similar chunks via FAISS.
        Falls back to keyword overlap if FAISS is unavailable.
        """
        if self._index is not None and self._model is not None:
            return self._retrieve_semantic(query, top_k)
        return self._retrieve_keyword(query, top_k)

    def _retrieve_semantic(self, query: str, top_k: int) -> List[Dict]:
        """FAISS-based semantic retrieval."""
        query_vec = self._model.encode([query], show_progress_bar=False)
        query_vec = np.array(query_vec, dtype="float32")

        k = min(top_k, len(self.chunks))
        distances, indices = self._index.search(query_vec, k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0:
                continue
            chunk = self.chunks[idx]
            results.append({
                "score": float(dist),
                "text": chunk["text"],
                "links": chunk["links"],
            })
        return results

    def _retrieve_keyword(self, query: str, top_k: int) -> List[Dict]:
        """Keyword-overlap fallback (preserves original behaviour)."""
        query_terms = set(re.findall(r"\w+", query.lower()))

        scored = []
        for chunk in self.chunks:
            chunk_terms = set(re.findall(r"\w+", chunk["text"].lower()))
            score = len(query_terms & chunk_terms)
            if score > 0:
                scored.append({
                    "score": score,
                    "text": chunk["text"],
                    "links": chunk["links"],
                })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    # =========================
    # Answer Formatting
    # =========================
    def build_answer(self, query: str) -> Dict:
        """
        Build a grounded answer with hyperlinks.
        Interface kept identical for app.py compatibility.
        """
        results = self.retrieve(query)

        if not results:
            return {
                "success": False,
                "answer": "No relevant information found in the scraped content.",
                "sources": []
            }

        answer_parts = []
        sources = []

        for idx, r in enumerate(results, start=1):
            answer_parts.append(f"{idx}. {r['text'][:500]}")
            for link in r["links"]:
                sources.append(link)

        # Remove duplicate links
        unique_sources = {
            src["url"]: src for src in sources
        }.values()

        return {
            "success": True,
            "answer": "\n\n".join(answer_parts),
            "sources": list(unique_sources)
        }
