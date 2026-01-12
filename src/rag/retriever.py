"""
RAG Retriever for CyraSoul content generation.
Combines embeddings and vector search for knowledge retrieval.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .embeddings import EmbeddingsClient
from .qdrant_client import QdrantVectorStore, SearchResult


@dataclass
class RetrievalResult:
    """Represents a retrieval result with source attribution."""
    content: str
    source: str
    collection: str
    score: float
    metadata: Dict[str, Any]


class RAGRetriever:
    """
    Retrieval-Augmented Generation retriever for CyraSoul.
    Handles knowledge retrieval from multiple collections.
    """

    def __init__(
        self,
        embeddings_client: Optional[EmbeddingsClient] = None,
        vector_store: Optional[QdrantVectorStore] = None
    ):
        """
        Initialize the RAG retriever.

        Args:
            embeddings_client: Optional pre-configured embeddings client.
            vector_store: Optional pre-configured vector store.
        """
        self.embeddings = embeddings_client or EmbeddingsClient()
        self.vector_store = vector_store or QdrantVectorStore()

    def retrieve(
        self,
        query: str,
        collections: Optional[List[str]] = None,
        top_k: int = 5,
        score_threshold: float = 0.7,
        rerank: bool = True,
        rerank_top_k: int = 3
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: Search query in Turkish or English.
            collections: List of collection keys to search. Default searches all.
            top_k: Number of results per collection before reranking.
            score_threshold: Minimum similarity score.
            rerank: Whether to rerank results across collections.
            rerank_top_k: Number of results to return after reranking.

        Returns:
            List of RetrievalResult objects sorted by relevance.
        """
        # Generate query embedding
        query_embedding = self.embeddings.embed_query(query)

        # Determine collections to search
        if collections is None:
            collections = list(QdrantVectorStore.COLLECTIONS.keys())

        # Search each collection
        all_results = []
        for collection_key in collections:
            try:
                results = self.vector_store.search(
                    collection_key=collection_key,
                    query_embedding=query_embedding,
                    top_k=top_k,
                    score_threshold=score_threshold
                )
                for result in results:
                    all_results.append(
                        RetrievalResult(
                            content=result.content,
                            source=result.id,
                            collection=collection_key,
                            score=result.score,
                            metadata=result.metadata
                        )
                    )
            except Exception as e:
                # Collection might not exist yet
                print(f"Warning: Could not search collection {collection_key}: {e}")

        # Sort by score
        all_results.sort(key=lambda x: x.score, reverse=True)

        # Rerank if enabled
        if rerank and len(all_results) > rerank_top_k:
            all_results = all_results[:rerank_top_k]

        return all_results

    def retrieve_for_topic(
        self,
        topic: str,
        content_type: str = "blog"
    ) -> Dict[str, List[RetrievalResult]]:
        """
        Retrieve all relevant knowledge for a content topic.

        Args:
            topic: Content topic in Turkish.
            content_type: Type of content (blog, product, social).

        Returns:
            Dict with categorized retrieval results.
        """
        results = {
            "wellness": [],
            "products": [],
            "scientific": [],
            "brand": []
        }

        # Search wellness for general topic knowledge
        results["wellness"] = self.retrieve(
            query=topic,
            collections=["wellness"],
            top_k=5,
            rerank_top_k=3
        )

        # Search products for relevant product mentions
        results["products"] = self.retrieve(
            query=topic,
            collections=["products"],
            top_k=3,
            rerank_top_k=2
        )

        # Search scientific for supporting evidence
        results["scientific"] = self.retrieve(
            query=f"bilimsel araştırma {topic}",  # "scientific research {topic}"
            collections=["scientific"],
            top_k=5,
            rerank_top_k=3
        )

        # Get brand voice guidelines
        results["brand"] = self.retrieve(
            query="marka sesi ton rehberi",  # "brand voice tone guide"
            collections=["brand"],
            top_k=2,
            rerank_top_k=1
        )

        return results

    def format_context(
        self,
        results: List[RetrievalResult],
        max_tokens: int = 2000
    ) -> str:
        """
        Format retrieval results into context string for the LLM.

        Args:
            results: List of retrieval results.
            max_tokens: Approximate maximum tokens in output.

        Returns:
            Formatted context string.
        """
        if not results:
            return ""

        context_parts = []
        estimated_tokens = 0

        for result in results:
            # Rough token estimation (4 chars per token for Turkish)
            result_tokens = len(result.content) // 4

            if estimated_tokens + result_tokens > max_tokens:
                break

            part = f"[Kaynak: {result.source} ({result.collection})]"
            part += f"\n{result.content}\n"
            context_parts.append(part)
            estimated_tokens += result_tokens

        return "\n---\n".join(context_parts)

    def format_topic_context(
        self,
        topic_results: Dict[str, List[RetrievalResult]]
    ) -> str:
        """
        Format topic retrieval results into structured context.

        Args:
            topic_results: Dict from retrieve_for_topic.

        Returns:
            Formatted context string for LLM.
        """
        sections = []

        if topic_results.get("wellness"):
            sections.append("## Wellness Bilgisi\n" + self.format_context(
                topic_results["wellness"], max_tokens=800
            ))

        if topic_results.get("products"):
            sections.append("## İlgili Ürünler\n" + self.format_context(
                topic_results["products"], max_tokens=400
            ))

        if topic_results.get("scientific"):
            sections.append("## Bilimsel Kaynaklar\n" + self.format_context(
                topic_results["scientific"], max_tokens=600
            ))

        if topic_results.get("brand"):
            sections.append("## Marka Rehberi\n" + self.format_context(
                topic_results["brand"], max_tokens=200
            ))

        return "\n\n".join(sections)
