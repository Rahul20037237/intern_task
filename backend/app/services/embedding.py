import os
import hashlib
from typing import List, Dict, Any

from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from ..core.logger import setup_logger  # adjust import paths
from ..config import settings
from ..core.cache_cls import CacheMemory

logger = setup_logger(name="embedding_service")


class EmbeddingService:
    def __init__(
        self,
        vb_path: str = "vector_db",
        model_name: str = "all-MiniLM-L6-v2",
        cache_file: str = "embedding_cache.pkl",
    ):
        try:
            self.vb_path = vb_path or settings.VECTOR_DB_PATH
            os.makedirs(self.vb_path, exist_ok=True)

            self.model = HuggingFaceEmbeddings(
                model_name=model_name,
                encode_kwargs={"normalize_embeddings": True}
            )

            self.cache = CacheMemory(cache_file)
        except Exception as e:
            logger.critical(f"Failed to initialize EmbeddingService: {e}")
            raise

    def _transform_to_documents(self, data_chunks: List[Dict[str, Any]]) -> List[Document]:
        documents = []
        try:
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
        except Exception as e:
            logger.error(f"Error transforming data chunks to documents: {e}")
        return documents

    def _get_cache_key(self, text: str) -> str:
        try:
            return hashlib.sha256(text.encode("utf-8")).hexdigest()
        except Exception as e:
            logger.error(f"Failed to generate cache key: {e}")
            return ""

    def _embed_texts_with_cache(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        texts_to_embed = []
        keys_to_embed = []

        try:
            for text in texts:
                key = self._get_cache_key(text)
                cached = self.cache.get(key)
                if cached is not None:
                    embeddings.append(cached["embedding"])
                else:
                    embeddings.append(None)
                    texts_to_embed.append(text)
                    keys_to_embed.append(key)

            if texts_to_embed:
                logger.info(f"Computing embeddings for {len(texts_to_embed)} uncached texts...")
                new_embeddings = self.model.embed_documents(texts_to_embed)

                idx = 0
                for i in range(len(embeddings)):
                    if embeddings[i] is None:
                        embeddings[i] = new_embeddings[idx]
                        try:
                            self.cache.set(keys_to_embed[idx], {"embedding": new_embeddings[idx]})
                        except Exception as e:
                            logger.warning(f"Failed to cache embedding for key {keys_to_embed[idx]}: {e}")
                        idx += 1
        except Exception as e:
            logger.error(f"Failed to embed texts: {e}")
            raise

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
