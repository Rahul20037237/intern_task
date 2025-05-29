from dataclasses import dataclass, field
from ..config import settings
from typing import Dict


@dataclass
class DatabaseAPI:
    bucket_name: str = field(default_factory=lambda: settings.BUCKET_NAME)

    @property
    def headers(self) -> Dict[str, str]:
        key = settings.SUPABASE_SERVICE_ROLE_KEY.get_secret_value()
        return {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/octet-stream",
            "x-upsert": "true"
        }
