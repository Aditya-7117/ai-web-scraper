import re
from typing import List, Dict


class RAGEngine:
    """
    Lightweight, domain-agnostic RAG engine.

    Responsibilities:
    - Chunk scraped content
    - Associate chunks with hyperlinks
    - Retrieve relevant chunks for a query
    - Return grounded answers with clickable sources
    """

    def __init__(self, content: str, links: List[Dict]):
        self.content = content
        self.links = links
        self.chunks = self._build_chunks()

    # =========================
    # Chunking
    # =========================
    def _build_chunks(self) -> List[Dict]:
        """
        Create text chunks and associate them with nearby links.
        """
        paragraphs = [
            p.strip() for p in self.content.split("\n")
            if len(p.strip()) > 40
        ]

        chunks = []
        for para in paragraphs:
            matched_links = []
            for link in self.links:
                if link["text"].lower() in para.lower():
                    matched_links.append(link)

            chunks.append({
                "text": para,
                "links": matched_links
            })

        return chunks

    # =========================
    # Retrieval
    # =========================
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve relevant chunks based on keyword overlap.
        """
        query_terms = set(
            re.findall(r"\w+", query.lower())
        )

        scored = []
        for chunk in self.chunks:
            chunk_terms = set(
                re.findall(r"\w+", chunk["text"].lower())
            )
            score = len(query_terms & chunk_terms)

            if score > 0:
                scored.append({
                    "score": score,
                    "text": chunk["text"],
                    "links": chunk["links"]
                })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    # =========================
    # Answer Formatting
    # =========================
    def build_answer(self, query: str) -> Dict:
        """
        Build a grounded answer with hyperlinks.
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
            answer_parts.append(f"{idx}. {r['text'][:300]}...")
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
