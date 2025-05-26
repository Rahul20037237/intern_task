import os
from typing import List, Dict

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface.embeddings import HuggingFaceEmbeddings

from ..config import settings
from ..core.logger import setup_logger

# Set Hugging Face token from your secret settings
os.environ["HUGGINGFACEHUB_API_TOKEN"] = settings.HUGGING_FACE_KEY.get_secret_value()

logger = setup_logger("query_service")


class QueryService:
    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.VECTOR_DB_PATH

        # Embedding model for vector store
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2",
            encode_kwargs={"normalize_embeddings": True}
        )

        # Initialize Chroma vector store
        self.vectorstore = Chroma(
            persist_directory=self.db_path,
            embedding_function=self.embedding_model
        )

    def query(self, user_query: str, k: int = 5) -> List[Dict]:
        try:
            logger.info(f"Running vector similarity search for: {user_query}")
            docs: List[Document] = self.vectorstore.similarity_search(user_query, k=k)
            logger.info(f"Retrieved {len(docs)} documents.")

            return [
                {
                    "text": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in docs
            ]
        except Exception as e:
            logger.error(f"Error in query: {e}", exc_info=True)
            return [{"error": str(e)}]
