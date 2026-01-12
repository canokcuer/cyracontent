"""
Document indexer for CyraSoul knowledge base.
Handles embedding and storing documents in Qdrant.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from .embeddings import EmbeddingsClient
from .qdrant_client import QdrantVectorStore, Document
from ..knowledge.loader import KnowledgeLoader, LoadedDocument, DocumentChunk


@dataclass
class IndexingResult:
    """Result of an indexing operation."""
    collection: str
    documents_processed: int
    chunks_indexed: int
    errors: List[str]


class KnowledgeIndexer:
    """
    Indexes knowledge base documents into Qdrant.
    """

    def __init__(
        self,
        embeddings_client: Optional[EmbeddingsClient] = None,
        vector_store: Optional[QdrantVectorStore] = None,
        loader: Optional[KnowledgeLoader] = None
    ):
        """
        Initialize the knowledge indexer.

        Args:
            embeddings_client: Optional pre-configured embeddings client.
            vector_store: Optional pre-configured vector store.
            loader: Optional pre-configured document loader.
        """
        self.embeddings = embeddings_client or EmbeddingsClient()
        self.vector_store = vector_store or QdrantVectorStore()
        self.loader = loader or KnowledgeLoader()

    def setup_collections(self) -> Dict[str, bool]:
        """
        Ensure all collections exist.

        Returns:
            Dict mapping collection names to whether they were created.
        """
        return self.vector_store.create_all_collections()

    def index_file(
        self,
        file_path: Path,
        collection_key: str,
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> IndexingResult:
        """
        Index a single file into a collection.

        Args:
            file_path: Path to the file.
            collection_key: Target collection key.
            extra_metadata: Additional metadata to add to chunks.

        Returns:
            IndexingResult with statistics.
        """
        errors = []

        try:
            # Load and chunk document
            doc = self.loader.load_file(file_path)

            # Add extra metadata to chunks
            if extra_metadata:
                for chunk in doc.chunks:
                    chunk.metadata.update(extra_metadata)

            # Generate embeddings for chunks
            chunk_texts = [chunk.content for chunk in doc.chunks]
            embeddings = self.embeddings.embed_texts(chunk_texts)

            # Create Document objects for storage
            documents = []
            for chunk, embedding in zip(doc.chunks, embeddings):
                documents.append(Document(
                    id=chunk.id,
                    content=chunk.content,
                    metadata=chunk.metadata,
                    embedding=embedding
                ))

            # Store in vector database
            self.vector_store.add_documents(collection_key, documents)

            return IndexingResult(
                collection=collection_key,
                documents_processed=1,
                chunks_indexed=len(documents),
                errors=errors
            )

        except Exception as e:
            errors.append(f"Error indexing {file_path}: {str(e)}")
            return IndexingResult(
                collection=collection_key,
                documents_processed=0,
                chunks_indexed=0,
                errors=errors
            )

    def index_directory(
        self,
        directory: Path,
        collection_key: str,
        recursive: bool = True,
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> IndexingResult:
        """
        Index all documents in a directory.

        Args:
            directory: Path to the directory.
            collection_key: Target collection key.
            recursive: Whether to search recursively.
            extra_metadata: Additional metadata to add to all chunks.

        Returns:
            Aggregated IndexingResult.
        """
        directory = Path(directory)
        total_docs = 0
        total_chunks = 0
        all_errors = []

        # Load all documents
        documents = self.loader.load_directory(directory, recursive=recursive)

        for doc in documents:
            # Add extra metadata
            if extra_metadata:
                for chunk in doc.chunks:
                    chunk.metadata.update(extra_metadata)

            try:
                # Generate embeddings
                chunk_texts = [chunk.content for chunk in doc.chunks]
                if not chunk_texts:
                    continue

                embeddings = self.embeddings.embed_texts(chunk_texts)

                # Create Document objects
                doc_objects = []
                for chunk, embedding in zip(doc.chunks, embeddings):
                    doc_objects.append(Document(
                        id=chunk.id,
                        content=chunk.content,
                        metadata=chunk.metadata,
                        embedding=embedding
                    ))

                # Store in vector database
                self.vector_store.add_documents(collection_key, doc_objects)

                total_docs += 1
                total_chunks += len(doc_objects)

            except Exception as e:
                all_errors.append(f"Error indexing {doc.filename}: {str(e)}")

        return IndexingResult(
            collection=collection_key,
            documents_processed=total_docs,
            chunks_indexed=total_chunks,
            errors=all_errors
        )

    def index_knowledge_base(
        self,
        base_path: Path
    ) -> Dict[str, IndexingResult]:
        """
        Index the entire knowledge base structure.

        Expected structure:
        base_path/
            wellness/       -> wellness collection
            products/       -> products collection
            scientific/     -> scientific collection
            brand/          -> brand collection

        Args:
            base_path: Path to the knowledge base root.

        Returns:
            Dict mapping collection keys to IndexingResult.
        """
        base_path = Path(base_path)
        results = {}

        # Map directory names to collection keys
        dir_to_collection = {
            "wellness": "wellness",
            "products": "products",
            "scientific": "scientific",
            "brand": "brand"
        }

        for dir_name, collection_key in dir_to_collection.items():
            dir_path = base_path / dir_name

            if dir_path.exists():
                print(f"Indexing {dir_path} -> {collection_key}...")
                results[collection_key] = self.index_directory(
                    directory=dir_path,
                    collection_key=collection_key,
                    extra_metadata={"category": dir_name}
                )
            else:
                results[collection_key] = IndexingResult(
                    collection=collection_key,
                    documents_processed=0,
                    chunks_indexed=0,
                    errors=[f"Directory not found: {dir_path}"]
                )

        return results

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about indexed collections.

        Returns:
            Dict with collection statistics.
        """
        stats = {}
        for key in QdrantVectorStore.COLLECTIONS:
            try:
                info = self.vector_store.get_collection_info(key)
                stats[key] = info
            except Exception as e:
                stats[key] = {"error": str(e)}
        return stats
