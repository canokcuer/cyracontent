"""
Embeddings module for CyraSoul content generation.
Uses Voyage AI for multilingual Turkish support.
"""

import os
from typing import List
import voyageai
from dotenv import load_dotenv

load_dotenv()


class EmbeddingsClient:
    """Client for generating text embeddings using Voyage AI."""

    def __init__(self, model: str = "voyage-multilingual-2"):
        """
        Initialize the embeddings client.

        Args:
            model: Voyage AI model to use. Default is voyage-multilingual-2 for Turkish support.
        """
        api_key = os.getenv("VOYAGE_API_KEY")
        if not api_key:
            raise ValueError("VOYAGE_API_KEY environment variable is required")

        self.client = voyageai.Client(api_key=api_key)
        self.model = model
        self.vector_size = 1024  # voyage-multilingual-2 output dimension

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text to embed.

        Returns:
            List of floats representing the embedding vector.
        """
        result = self.client.embed(
            texts=[text],
            model=self.model,
            input_type="document"
        )
        return result.embeddings[0]

    def embed_texts(self, texts: List[str], batch_size: int = 128) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed.
            batch_size: Number of texts to embed per API call.

        Returns:
            List of embedding vectors.
        """
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            result = self.client.embed(
                texts=batch,
                model=self.model,
                input_type="document"
            )
            all_embeddings.extend(result.embeddings)

        return all_embeddings

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.
        Uses 'query' input type for better retrieval performance.

        Args:
            query: Search query to embed.

        Returns:
            List of floats representing the embedding vector.
        """
        result = self.client.embed(
            texts=[query],
            model=self.model,
            input_type="query"
        )
        return result.embeddings[0]
