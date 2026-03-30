import os
import json
from typing import List, Dict, Any
from utils.logger import logger_instance as logger

class VectorStore:
    """
    Basic ephemeral vector store for agent memory.
    Can be extended to use ChromaDB or other vector databases.
    """
    def __init__(self, persist_path=None):
        self.persist_path = persist_path or os.getenv("VECTOR_STORE_PATH", "./data/chroma_db")
        self.memory_store = []
        self._ensure_dir()

    def _ensure_dir(self):
        if not os.path.exists(self.persist_path):
            os.makedirs(self.persist_path)
            logger.info(f"Vector store directory created at {self.persist_path}")

    def add_memory(self, text: str, metadata: Dict[str, Any] = None, embedding: List[float] = None):
        """Add a memory entry with optional embedding"""
        memory_entry = {
            "text": text,
            "metadata": metadata or {},
            "embedding": embedding or [],
            "timestamp": str(os.times())
        }
        self.memory_store.append(memory_entry)
        logger.debug(f"Memory added: {text[:50]}...")

    def search_similar(self, query_embedding: List[float], top_k: int = 5) -> List[Dict]:
        """
        Search for similar memories using cosine similarity.
        Returns top_k most similar entries.
        """
        if not query_embedding:
            return []

        # Simple cosine similarity calculation
        def cosine_similarity(vec1, vec2):
            if not vec1 or not vec2:
                return 0.0
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = sum(a * a for a in vec1) ** 0.5
            magnitude2 = sum(b * b for b in vec2) ** 0.5
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            return dot_product / (magnitude1 * magnitude2)

        # Calculate similarities
        results = []
        for memory in self.memory_store:
            if memory.get("embedding"):
                similarity = cosine_similarity(query_embedding, memory["embedding"])
                results.append({
                    "text": memory["text"],
                    "metadata": memory["metadata"],
                    "similarity": similarity
                })

        # Sort by similarity and return top_k
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def get_all_memories(self) -> List[Dict]:
        """Retrieve all stored memories"""
        return self.memory_store

    def clear_memories(self):
        """Clear all memories from the store"""
        self.memory_store = []
        logger.info("Vector store cleared")

# Global instance
vector_store = VectorStore()
