import os
import hashlib
import logging
import re
from datetime import datetime
from typing import List, Dict, Any

import tiktoken
from .ocr_extract import OCRTextExtractor
from ..app.core.cache_cls import CacheMemory

logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')
logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, file_path="dataset/", extensions=('pdf', 'png', 'jpg', 'jpeg'), cache_file="ocr_cache.pkl"):
        self.file_path = file_path
        self.extensions = extensions
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.cache = CacheMemory(cache_file)
        self._entities = [
            os.path.join(self.file_path, f)
            for f in os.listdir(self.file_path)
            if f.lower().endswith(self.extensions)
        ]

    def _hash_file(self, path: str) -> str | None:
        sha = hashlib.sha256()
        try:
            with open(path, 'rb') as f:
                while chunk := f.read(8192):
                    sha.update(chunk)
            return sha.hexdigest()
        except Exception as e:
            logger.warning(f"Hashing failed for {path}: {e}")
            return None

    def _chunk_text(self, text: str, page: int, max_tokens: int = 500) -> List[Dict[str, Any]]:
        sentences = re.split(r'(?<=[.!?]) +', text)
        chunks = []
        current_chunk = ""
        para_index = 1

        for sentence in sentences:
            candidate = (current_chunk + " " + sentence).strip() if current_chunk else sentence
            if len(self.tokenizer.encode(candidate)) <= max_tokens:
                current_chunk = candidate
            else:
                chunks.append({
                    "text": current_chunk,
                    "page": page,
                    "paragraph": para_index,
                    "tokens": len(self.tokenizer.encode(current_chunk)),
                    "embedding": None
                })
                current_chunk = sentence
                para_index += 1

        if current_chunk:
            chunks.append({
                "text": current_chunk,
                "page": page,
                "paragraph": para_index,
                "tokens": len(self.tokenizer.encode(current_chunk)),
                "embedding": None
            })

        return chunks

    def read_and_process(self) -> List[Dict[str, Any]]:
        extractor = OCRTextExtractor()
        results = []

        for path in self._entities:
            file_hash = self._hash_file(path)
            if not file_hash:
                continue

            cached_entry = self.cache.get(file_hash)
            if cached_entry:
                if isinstance(cached_entry, str):
                    logger.warning(f"Legacy cache format for {path}, converting...")
                    file_data = {
                        "file_path": path,
                        "file_hash": file_hash,
                        "chunks": self._chunk_text(cached_entry, page=1)
                    }
                else:
                    file_data = cached_entry
                logger.info(f"Using cached data for {path}")
            else:
                ext = os.path.splitext(path)[-1].lower()
                pages = extractor.ocr_pdf(path) if ext == ".pdf" else extractor.ocr_image(path)

                file_data = {
                    "file_path": path,
                    "file_hash": file_hash,
                    "chunks": []
                }

                for page_num, page_text in pages:
                    file_data["chunks"].extend(self._chunk_text(page_text, page_num))

                self.cache.set(file_hash, file_data)

            file_stat = os.stat(path)
            file_data["meta"] = {
                "filename": os.path.basename(path),
                "upload_date": datetime.fromtimestamp(file_stat.st_ctime).isoformat(),
                "file_size": file_stat.st_size
            }

            results.append(file_data)

        return results


if __name__ == "__main__":
    loader = DataLoader(file_path="dataset")
    processed_files = loader.read_and_process()

    for file_entry in processed_files:
        print(f"\nFile: {file_entry['meta']['filename']}")
        print(f"Uploaded: {file_entry['meta']['upload_date']}")
        print(f"Size: {file_entry['meta']['file_size']} bytes")
        print(f"Hash: {file_entry['file_hash']}")
        for i, chunk in enumerate(file_entry["chunks"][:2], 1):  # Display only first 2 chunks
            print(f"Chunk {i} (Page {chunk['page']}): {chunk['text'][:60]}... [{chunk['tokens']} tokens]")
