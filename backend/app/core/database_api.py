from dataclasses import dataclass, field
from ..config import settings
from typing import Dict
import requests
from supabase import create_client,Client

@dataclass
class DocDatabase:
    bucket_name: str = field(default_factory=lambda: settings.BUCKET_NAME)
    supabase:Client=create_client(settings.SUPABASE_URL,settings.SUPABASE_SERVICE_ROLE_KEY)

    def upload_file(self, path: str, cache_data: bytes) -> bool:
        upload_url = f'public/{path}'

        try:
            response = (
                self.supabase.
                storage.from_(self.bucket_name).
                upload(file=cache_data,path=upload_url,
                       file_options={"cache-control": "3600", "upsert": False})
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            print(f"Upload failed: {e} - Response: {getattr(e.response, 'text', '')}")
            return False

    def read_file(self, path: str) -> bytes | None:
        download_url = f'public/{path}'
        try:
            response = (
                self.supabase.storage.from_(self.bucket_name).download(download_url)
            )
            response.raise_for_status()
            return response.content  # Returns the raw bytes of the file
        except requests.RequestException as e:
            print(f"Download failed: {e} - Response: {getattr(e.response, 'text', '')}")
            return None




# class ApiDatabase:


