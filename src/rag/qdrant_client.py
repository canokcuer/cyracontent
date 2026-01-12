"""
Qdrant vector database client for CyraSoul content generation.
"""

import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Document:
    """Represents a document in the knowledge base."""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


@dataclass
class SearchResult:
    """Represents a search result from the vector database."""
    id: str
    content: str
    metadata: Dict[str, Any]
    score: float


class QdrantVectorStore:
    """Vector store implementation using Qdrant."""

    # Collection configurations
    COLLECTIONS = {
        "wellness": {
            "name": "cyrasoul_wellness",
            "description": "Wellness tips, health guides, lifestyle content"
        },
        "products": {
            "name": "cyrasoul_products",
            "description": "Product information, ingredients, benefits"
        },
        "scientific": {
            "name": "cyrasoul_scientific",
            "description": "Scientific references, research papers, citations"
        },
        "brand": {
            "name": "cyrasoul_brand",
            "description": "Brand voice, tone guidelines, messaging"
        }
    }

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        api_key: Optional[str] = None,
        vector_size: int = 1024
    ):
        """
        Initialize the Qdrant vector store.

        Args:
            host: Qdrant host. Defaults to QDRANT_HOST env var or localhost.
            port: Qdrant port. Defaults to QDRANT_PORT env var or 6333.
            api_key: Qdrant API key for cloud. Defaults to QDRANT_API_KEY env var.
            vector_size: Size of embedding vectors. Default 1024 for Voyage AI.
        """
        self.host = host or os.getenv("QDRANT_HOST", "localhost")
        self.port = int(port or os.getenv("QDRANT_PORT", 6333))
        # Handle empty string as no API key
        self.api_key = api_key or os.getenv("QDRANT_API_KEY") or None
        if self.api_key and not self.api_key.strip():
            self.api_key = None
        self.vector_size = vector_size

        # Initialize client
        if self.api_key:
            # Cloud connection
            self.client = QdrantClient(
                url=f"https://{self.host}",
                api_key=self.api_key
            )
        else:
            # Local connection - explicitly use HTTP URL
            self.client = QdrantClient(
                url=f"http://{self.host}:{self.port}"
            )

    def create_collection(self, collection_key: str) -> bool:
        """
        Create a collection if it doesn't exist.

        Args:
            collection_key: Key from COLLECTIONS dict (wellness, products, etc.)

        Returns:
            True if created, False if already exists.
        """
        if collection_key not in self.COLLECTIONS:
            raise ValueError(f"Unknown collection: {collection_key}")

        collection_name = self.COLLECTIONS[collection_key]["name"]

        # Check if collection exists
        collections = self.client.get_collections().collections
        if any(c.name == collection_name for c in collections):
            return False

        # Create collection
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=self.vector_size,
                distance=Distance.COSINE
            )
        )
        return True

    def create_all_collections(self) -> Dict[str, bool]:
        """
        Create all defined collections.

        Returns:
            Dict mapping collection keys to creation status.
        """
        results = {}
        for key in self.COLLECTIONS:
            results[key] = self.create_collection(key)
        return results

    def add_documents(
        self,
        collection_key: str,
        documents: List[Document]
    ) -> int:
        """
        Add documents with embeddings to a collection.

        Args:
            collection_key: Key from COLLECTIONS dict.
            documents: List of Document objects with embeddings.

        Returns:
            Number of documents added.
        """
        if collection_key not in self.COLLECTIONS:
            raise ValueError(f"Unknown collection: {collection_key}")

        collection_name = self.COLLECTIONS[collection_key]["name"]

        points = []
        for doc in documents:
            if doc.embedding is None:
                raise ValueError(f"Document {doc.id} has no embedding")

            point = PointStruct(
                id=hash(doc.id) % (2**63),  # Convert string ID to int
                vector=doc.embedding,
                payload={
                    "doc_id": doc.id,
                    "content": doc.content,
                    **doc.metadata
                }
            )
            points.append(point)

        self.client.upsert(
            collection_name=collection_name,
            points=points
        )
        return len(points)

    def search(
        self,
        collection_key: str,
        query_embedding: List[float],
        top_k: int = 5,
        score_threshold: float = 0.0,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar documents in a collection.

        Args:
            collection_key: Key from COLLECTIONS dict.
            query_embedding: Query vector.
            top_k: Number of results to return.
            score_threshold: Minimum similarity score.
            filter_metadata: Optional metadata filters.

        Returns:
            List of SearchResult objects.
        """
        if collection_key not in self.COLLECTIONS:
            raise ValueError(f"Unknown collection: {collection_key}")

        collection_name = self.COLLECTIONS[collection_key]["name"]

        # Build filter if provided
        query_filter = None
        if filter_metadata:
            conditions = []
            for key, value in filter_metadata.items():
                conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            query_filter = Filter(must=conditions)

        # Search using query_points (new Qdrant API)
        results = self.client.query_points(
            collection_name=collection_name,
            query=query_embedding,
            limit=top_k,
            score_threshold=score_threshold,
            query_filter=query_filter
        )

        # Convert to SearchResult objects
        search_results = []
        for result in results.points:
            payload = result.payload or {}
            search_results.append(
                SearchResult(
                    id=payload.get("doc_id", str(result.id)),
                    content=payload.get("content", ""),
                    metadata={k: v for k, v in payload.items() if k not in ["doc_id", "content"]},
                    score=result.score
                )
            )

        return search_results

    def search_all_collections(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        score_threshold: float = 0.0
    ) -> Dict[str, List[SearchResult]]:
        """
        Search across all collections.

        Args:
            query_embedding: Query vector.
            top_k: Number of results per collection.
            score_threshold: Minimum similarity score.

        Returns:
            Dict mapping collection keys to search results.
        """
        results = {}
        for key in self.COLLECTIONS:
            try:
                results[key] = self.search(
                    collection_key=key,
                    query_embedding=query_embedding,
                    top_k=top_k,
                    score_threshold=score_threshold
                )
            except Exception:
                results[key] = []
        return results

    def delete_collection(self, collection_key: str) -> bool:
        """
        Delete a collection.

        Args:
            collection_key: Key from COLLECTIONS dict.

        Returns:
            True if deleted.
        """
        if collection_key not in self.COLLECTIONS:
            raise ValueError(f"Unknown collection: {collection_key}")

        collection_name = self.COLLECTIONS[collection_key]["name"]
        self.client.delete_collection(collection_name=collection_name)
        return True

    def get_collection_info(self, collection_key: str) -> Dict[str, Any]:
        """
        Get information about a collection.

        Args:
            collection_key: Key from COLLECTIONS dict.

        Returns:
            Collection information.
        """
        if collection_key not in self.COLLECTIONS:
            raise ValueError(f"Unknown collection: {collection_key}")

        collection_name = self.COLLECTIONS[collection_key]["name"]
        info = self.client.get_collection(collection_name=collection_name)

        return {
            "name": collection_name,
            "points_count": info.points_count or 0,
            "status": info.status
        }
