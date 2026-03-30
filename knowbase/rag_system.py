import os
from typing import List, Dict, Any
from memory.vector_store import vector_store
from services.hf_service import hf_service
from utils.logger import logger_instance as logger

class RAGSystem:
    """
    Retrieval-Augmented Generation system for knowledge retrieval.
    Integrates with vector store and embedding service.
    """
    def __init__(self):
        self.vector_store = vector_store
        self.embedding_service = hf_service

    async def add_knowledge(self, text: str, metadata: Dict[str, Any] = None):
        """Add knowledge to the vector store with embeddings"""
        try:
            # Get embeddings for the text
            embedding = await self.embedding_service.get_embeddings(text)
            
            # Store in vector database
            self.vector_store.add_memory(text, metadata, embedding)
            logger.info(f"Knowledge added: {text[:50]}...")
            return True
        except Exception as e:
            logger.error(f"Error adding knowledge: {str(e)}")
            return False

    async def retrieve_relevant_knowledge(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve relevant knowledge based on query.
        Returns top_k most relevant entries.
        """
        try:
            # Get query embedding
            query_embedding = await self.embedding_service.get_embeddings(query)
            
            if not query_embedding:
                logger.warning("Failed to generate query embedding")
                return []

            # Search for similar entries
            results = self.vector_store.search_similar(query_embedding, top_k)
            logger.info(f"Retrieved {len(results)} relevant knowledge entries")
            return results
        except Exception as e:
            logger.error(f"Error retrieving knowledge: {str(e)}")
            return []

    def get_context_for_prompt(self, query: str, results: List[Dict]) -> str:
        """
        Format retrieved knowledge into context string for LLM prompt.
        """
        if not results:
            return ""

        context_parts = ["Relevant knowledge:"]
        for i, result in enumerate(results, 1):
            context_parts.append(f"\n{i}. {result['text']}")
            if result.get('similarity'):
                context_parts.append(f" (relevance: {result['similarity']:.2f})")

        return "\n".join(context_parts)

# Global instance
rag_system = RAGSystem()
