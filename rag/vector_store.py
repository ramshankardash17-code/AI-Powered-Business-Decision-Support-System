"""
RAG Vector Store & Document Chunking Engine
Enterprise AI Business Decision Intelligence Platform
Chunks Corporate Policy Documents & Computes Cosine Similarity Search
"""
import re
import logging
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from config.settings import settings

logger = logging.getLogger(__name__)

class DocumentChunk:
    def __init__(self, doc_name: str, title: str, section: str, content: str, chunk_id: str):
        self.doc_name = doc_name
        self.title = title
        self.section = section
        self.content = content
        self.chunk_id = chunk_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "document": self.doc_name,
            "section": self.section,
            "content": self.content
        }

class PolicyVectorStore:
    def __init__(self, docs_dir: Path = None):
        self.docs_dir = docs_dir or settings.DOCUMENTS_DIR
        self.chunks: List[DocumentChunk] = []
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.tfidf_matrix = None
        self._is_indexed = False

    def load_and_index_documents(self):
        """Loads all Markdown policy files from data/documents, chunks, and creates vector index"""
        logger.info(f"Indexing RAG knowledge documents from {self.docs_dir}...")
        self.chunks = []
        
        md_files = list(self.docs_dir.glob("*.md"))
        if not md_files:
            logger.warning(f"No Markdown files found in {self.docs_dir}")
            return

        chunk_counter = 1
        for file_path in md_files:
            text = file_path.read_text(encoding="utf-8")
            doc_name = file_path.name
            
            # Extract main title
            title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
            doc_title = title_match.group(1).strip() if title_match else doc_name

            # Split by markdown H2 (##)
            sections = re.split(r"\n(?=##\s+)", text)
            for sec in sections:
                sec = sec.strip()
                if not sec:
                    continue
                sec_header_match = re.search(r"^##\s+(.+)$", sec, re.MULTILINE)
                section_title = sec_header_match.group(1).strip() if sec_header_match else "Overview"
                
                # Clean content
                cleaned_content = re.sub(r"^##\s+.+$", "", sec, flags=re.MULTILINE).strip()
                if len(cleaned_content) < 30:
                    continue

                chunk = DocumentChunk(
                    doc_name=doc_name,
                    title=doc_title,
                    section=section_title,
                    content=cleaned_content,
                    chunk_id=f"CHK_{chunk_counter:04d}"
                )
                self.chunks.append(chunk)
                chunk_counter += 1

        if not self.chunks:
            logger.warning("No valid chunks extracted from documents.")
            return

        # Vectorize corpus
        corpus = [f"{c.title} {c.section} {c.content}" for c in self.chunks]
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        self._is_indexed = True
        logger.info(f"Successfully indexed {len(self.chunks)} knowledge chunks from {len(md_files)} documents.")

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """Executes cosine similarity query against indexed policy chunks"""
        if not self._is_indexed:
            self.load_and_index_documents()

        if not self.chunks or self.tfidf_matrix is None:
            return []

        query_vec = self.vectorizer.transform([query])
        # Compute cosine similarity: (A . B) / (|A| * |B|)
        cosine_sim = (self.tfidf_matrix * query_vec.T).toarray().flatten()

        # Get top-k indices
        top_indices = np.argsort(cosine_sim)[::-1][:top_k]

        results = []
        for idx in top_indices:
            score = float(cosine_sim[idx])
            if score > 0.05: # Minimum relevance threshold
                chunk = self.chunks[idx]
                results.append({
                    "chunk_id": chunk.chunk_id,
                    "document": chunk.doc_name,
                    "title": chunk.title,
                    "section": chunk.section,
                    "content": chunk.content,
                    "relevance_score": round(score, 3)
                })

        return results

# Singleton vector store instance
policy_vector_store = PolicyVectorStore()
policy_vector_store.load_and_index_documents()

if __name__ == "__main__":
    test_res = policy_vector_store.search("What is our return policy for electronics?")
    for r in test_res:
        print(f"[{r['document']}] {r['section']} (Score: {r['relevance_score']}):\n{r['content']}\n")
