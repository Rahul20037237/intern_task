import os
import hashlib
from typing import List, Dict, Any

from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from ..core.logger import setup_logger # adjust import paths
from ..config import settings
from ..core.cache_cls import  CacheMemory


logger = setup_logger(name="embedding_service")


class EmbeddingService:
    def __init__(
        self,
        vb_path: str = "vector_db",
        model_name: str = "all-MiniLM-L6-v2",
        cache_file: str = "embedding_cache.pkl",
    ):
        self.vb_path = vb_path or settings.VECTOR_DB_PATH
        os.makedirs(self.vb_path, exist_ok=True)

        # LangChain HuggingFace embeddings wrapper
        self.model = HuggingFaceEmbeddings(
            model_name=model_name,
            encode_kwargs={"normalize_embeddings": True}
        )

        # Initialize your cache
        self.cache = CacheMemory(cache_file)

    def _transform_to_documents(self, data_chunks: List[Dict[str, Any]]) -> List[Document]:
        documents = []
        for file in data_chunks:
            metadata = file.get("meta", {})
            for chunk in file.get("chunks", []):
                documents.append(
                    Document(
                        page_content=chunk.get("text", ""),
                        metadata={
                            "filename": metadata.get("filename", "unknown"),
                            "page": chunk.get("page", -1),
                            "paragraph": chunk.get("paragraph", -1)
                        }
                    )
                )
        logger.info(f"Transformed {len(documents)} chunks into LangChain Documents.")
        return documents

    def _get_cache_key(self, text: str) -> str:
        """Generate a hash key for caching based on text content."""
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def _embed_texts_with_cache(self, texts: List[str]) -> List[List[float]]:
        """Embed texts using cache to avoid recomputing embeddings for same texts."""
        embeddings = []
        texts_to_embed = []
        keys_to_embed = []

        # Check cache for each text embedding
        for text in texts:
            key = self._get_cache_key(text)
            cached = self.cache.get(key)
            if cached is not None:
                embeddings.append(cached["embedding"])
            else:
                embeddings.append(None)  # placeholder
                texts_to_embed.append(text)
                keys_to_embed.append(key)

        # Compute embeddings only for texts not cached
        if texts_to_embed:
            logger.info(f"Computing embeddings for {len(texts_to_embed)} uncached texts...")
            # Note: embed_documents returns a list of embeddings
            new_embeddings = self.model.embed_documents(texts_to_embed)

            idx = 0
            for i in range(len(embeddings)):
                if embeddings[i] is None:
                    embeddings[i] = new_embeddings[idx]
                    self.cache.set(keys_to_embed[idx], {"embedding": new_embeddings[idx]})
                    idx += 1

        return embeddings

    def build_and_save_vectorstore(self, data_chunks: List[Dict[str, Any]]):
        try:
            documents = self._transform_to_documents(data_chunks)
            texts = [doc.page_content for doc in documents]

            logger.info("Embedding texts with cache...")
            embeddings = self._embed_texts_with_cache(texts)

            logger.info("Creating Chroma vector store...")
            db = Chroma.from_documents(
                documents=documents,
                embedding=self.model,
                persist_directory=self.vb_path
            )

            logger.info(f"Vectorstore saved to '{self.vb_path}' with {len(documents)} documents.")

        except Exception as e:
            logger.error(f"Failed to build and save vectorstore: {e}")
            raise

