"""
RAG Pipeline Module.

Handles:
1. Document loading (PDF, Markdown, TXT)
2. Text chunking with metadata
3. Embedding generation (Google or Sentence Transformers)
4. ChromaDB vector storage
5. Similarity search with confidence scores
"""

import os
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    TextLoader,
)
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """A single retrieved chunk with metadata and score."""
    content: str
    source: str          # Source document filename
    page_or_section: str # Page number (PDF) or section heading (MD)
    score: float         # Similarity score (0-1, higher = more relevant)
    article_id: str      # Extracted article ID if present


@dataclass
class RAGResponse:
    """Complete RAG response with all retrieved chunks."""
    query: str
    results: list[RetrievalResult]
    top_score: float     # Highest similarity score
    is_confident: bool   # Whether retrieval confidence is above threshold
    context_text: str    # Formatted context for LLM


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline using ChromaDB + Google Embeddings.
    Falls back to Sentence Transformers if no Google API key is available.
    """

    def __init__(self):
        from app.config import config
        self.config = config
        self._vectorstore = None
        self._embeddings = None
        self._init_embeddings()

    def _init_embeddings(self):
        """Initialize embedding model."""
        try:
            if (self.config.embedding.provider == "google"
                    and self.config.llm.google_api_key):
                from langchain_google_genai import GoogleGenerativeAIEmbeddings
                self._embeddings = GoogleGenerativeAIEmbeddings(
                    model=self.config.embedding.model_name,
                    google_api_key=self.config.llm.google_api_key,
                )
                logger.info("RAG: Using Google Generative AI Embeddings")
            else:
                raise ValueError("Google API key not available")
        except Exception as e:
            logger.warning(f"RAG: Google embeddings failed ({e}), falling back to SentenceTransformers")
            try:
                from langchain_community.embeddings import SentenceTransformerEmbeddings
                self._embeddings = SentenceTransformerEmbeddings(
                    model_name="all-MiniLM-L6-v2"
                )
                logger.info("RAG: Using SentenceTransformers (all-MiniLM-L6-v2)")
            except Exception as e2:
                logger.error(f"RAG: SentenceTransformers also failed: {e2}")
                raise RuntimeError(
                    "No embedding model available. Install 'sentence-transformers' or set GOOGLE_API_KEY."
                )

    def _load_documents(self, data_dir: str) -> list[Document]:
        """
        Load all supported documents from the data directory.
        Supported: .pdf, .md, .txt
        """
        data_path = Path(data_dir)
        if not data_path.exists():
            raise FileNotFoundError(f"Data directory not found: {data_dir}")

        documents = []
        loaded_files = []
        failed_files = []

        for file_path in sorted(data_path.iterdir()):
            suffix = file_path.suffix.lower()
            if suffix not in (".pdf", ".md", ".txt", ".markdown"):
                continue

            try:
                if suffix == ".pdf":
                    loader = PyPDFLoader(str(file_path))
                    docs = loader.load()
                    # Add page numbers to metadata
                    for doc in docs:
                        doc.metadata["source_file"] = file_path.name
                        doc.metadata["page_or_section"] = f"Page {doc.metadata.get('page', 0) + 1}"

                elif suffix in (".md", ".markdown"):
                    # Use TextLoader for markdown — more reliable
                    loader = TextLoader(str(file_path), encoding="utf-8")
                    docs = loader.load()
                    for doc in docs:
                        doc.metadata["source_file"] = file_path.name
                        # Extract first heading as section name
                        section = self._extract_first_heading(doc.page_content)
                        doc.metadata["page_or_section"] = section

                elif suffix == ".txt":
                    loader = TextLoader(str(file_path), encoding="utf-8")
                    docs = loader.load()
                    for doc in docs:
                        doc.metadata["source_file"] = file_path.name
                        doc.metadata["page_or_section"] = "Section 1"

                else:
                    continue

                documents.extend(docs)
                loaded_files.append(file_path.name)
                logger.info(f"RAG: Loaded {file_path.name} → {len(docs)} doc(s)")

            except Exception as e:
                failed_files.append(file_path.name)
                logger.error(f"RAG: Failed to load {file_path.name}: {e}")

        logger.info(
            f"RAG: Document loading complete. "
            f"Loaded: {len(loaded_files)} files, Failed: {len(failed_files)}"
        )

        if not documents:
            raise RuntimeError(
                f"No documents loaded from {data_dir}. "
                "Run ingestion after adding documents to the /data directory."
            )

        return documents

    @staticmethod
    def _extract_first_heading(text: str) -> str:
        """Extract the first markdown heading from text."""
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("#"):
                return line.lstrip("#").strip()[:80]
        return "Overview"

    @staticmethod
    def _extract_article_id(text: str) -> str:
        """Try to extract article ID like 'API-001' from document content."""
        import re
        match = re.search(r"\b([A-Z]{2,4}-\d{3})\b", text[:500])
        return match.group(1) if match else "N/A"

    def ingest(self, data_dir: Optional[str] = None) -> dict:
        """
        Load, chunk, embed, and store all documents.
        Returns statistics about the ingestion process.
        """
        from langchain_community.vectorstores import Chroma

        data_dir = data_dir or self.config.rag.data_directory

        logger.info(f"RAG: Starting ingestion from {data_dir}")

        # Load documents
        raw_docs = self._load_documents(data_dir)

        # Chunk documents
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.rag.chunk_size,
            chunk_overlap=self.config.rag.chunk_overlap,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
            length_function=len,
        )
        chunks = splitter.split_documents(raw_docs)

        # Preserve and enrich metadata
        for chunk in chunks:
            if "source_file" not in chunk.metadata:
                chunk.metadata["source_file"] = "unknown"
            if "page_or_section" not in chunk.metadata:
                chunk.metadata["page_or_section"] = "N/A"
            chunk.metadata["article_id"] = self._extract_article_id(chunk.page_content)

        logger.info(f"RAG: Created {len(chunks)} chunks from {len(raw_docs)} documents")

        # Store in ChromaDB
        os.makedirs(self.config.vector_db.persist_directory, exist_ok=True)

        self._vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self._embeddings,
            persist_directory=self.config.vector_db.persist_directory,
            collection_name=self.config.vector_db.collection_name,
        )

        logger.info(
            f"RAG: Ingestion complete. "
            f"Stored {len(chunks)} chunks in ChromaDB at {self.config.vector_db.persist_directory}"
        )

        return {
            "documents_loaded": len(set(c.metadata.get("source_file", "") for c in chunks)),
            "chunks_created": len(chunks),
            "persist_directory": self.config.vector_db.persist_directory,
        }

    def load_existing(self) -> bool:
        """
        Load an existing ChromaDB vector store.
        Returns True if successful, False if not found.
        """
        from langchain_community.vectorstores import Chroma

        persist_dir = self.config.vector_db.persist_directory
        if not os.path.exists(persist_dir):
            logger.warning(f"RAG: No existing vector store at {persist_dir}")
            return False

        try:
            self._vectorstore = Chroma(
                persist_directory=persist_dir,
                embedding_function=self._embeddings,
                collection_name=self.config.vector_db.collection_name,
            )
            count = self._vectorstore._collection.count()
            logger.info(f"RAG: Loaded existing vector store with {count} chunks")
            return count > 0
        except Exception as e:
            logger.error(f"RAG: Failed to load existing vector store: {e}")
            return False

    def retrieve(self, query: str, top_k: Optional[int] = None) -> RAGResponse:
        """
        Retrieve the most relevant document chunks for a query.

        Args:
            query: User's question or message
            top_k: Number of chunks to retrieve (default from config)

        Returns:
            RAGResponse with retrieved chunks and confidence assessment
        """
        if self._vectorstore is None:
            raise RuntimeError(
                "Vector store not loaded. Run ingest() first or call load_existing()."
            )

        k = top_k or self.config.rag.top_k

        try:
            # Retrieve with similarity scores
            results_with_scores = self._vectorstore.similarity_search_with_score(
                query, k=k
            )
        except Exception as e:
            logger.error(f"RAG: Retrieval failed: {e}")
            return RAGResponse(
                query=query,
                results=[],
                top_score=0.0,
                is_confident=False,
                context_text="No relevant information found in the knowledge base.",
            )

        if not results_with_scores:
            return RAGResponse(
                query=query,
                results=[],
                top_score=0.0,
                is_confident=False,
                context_text="No relevant information found in the knowledge base.",
            )

        retrieval_results = []
        for doc, raw_score in results_with_scores:
            # ChromaDB returns L2 distance (lower = better)
            # Convert to similarity score (0-1, higher = better)
            # Using: similarity = 1 / (1 + distance)
            similarity = 1.0 / (1.0 + raw_score)

            retrieval_results.append(RetrievalResult(
                content=doc.page_content,
                source=doc.metadata.get("source_file", "Unknown"),
                page_or_section=doc.metadata.get("page_or_section", "N/A"),
                score=round(similarity, 4),
                article_id=doc.metadata.get("article_id", "N/A"),
            ))

        # Sort by score descending
        retrieval_results.sort(key=lambda x: x.score, reverse=True)
        top_score = retrieval_results[0].score if retrieval_results else 0.0

        is_confident = top_score >= self.config.rag.min_similarity_score

        # Build context text for LLM
        context_parts = []
        for i, result in enumerate(retrieval_results, 1):
            context_parts.append(
                f"[Source {i}: {result.source} | {result.page_or_section} | Score: {result.score:.2f}]\n"
                f"{result.content}"
            )
        context_text = "\n\n---\n\n".join(context_parts)

        return RAGResponse(
            query=query,
            results=retrieval_results,
            top_score=top_score,
            is_confident=is_confident,
            context_text=context_text,
        )

    def is_ready(self) -> bool:
        """Check if the vector store is ready for retrieval."""
        if self._vectorstore is None:
            return False
        try:
            count = self._vectorstore._collection.count()
            return count > 0
        except Exception:
            return False


# Module-level singleton
_pipeline: Optional[RAGPipeline] = None


def get_pipeline() -> RAGPipeline:
    """Get or create the singleton RAGPipeline."""
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
        # Try to load existing store
        _pipeline.load_existing()
    return _pipeline
