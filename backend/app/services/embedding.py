# services/embedding_service.py

import os
from typing import List, Dict, Any
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from ..core.logger import setup_logger
from  ..config import settings
logger=setup_logger(name="embedding_service")
class EmbeddingService:
    def __init__(self, vb_path: str = "vector_db", model_name: str = "text-embedding-3-small"):
        self.vb_path = vb_path or settings.VECTOR_DB_PATH
        os.environ["OPENAI_API_KEY"] = (settings.OPENAI_API_KEY.get_secret_value())
        self.embedding_model = OpenAIEmbeddings(model=model_name)
        os.makedirs(vb_path, exist_ok=True)

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

    def build_and_save_vectorstore(self, data_chunks: List[Dict[str, Any]]):
        try:
            documents = self._transform_to_documents(data_chunks)
            db = FAISS.from_documents(documents, self.embedding_model)
            db.save_local(self.vb_path)
            logger.info(f"Vectorstore saved to '{self.vb_path}' with {len(documents)} documents.")
        except Exception as e:
            logger.error(f"Failed to build and save vectorstore: {e}")
            raise
