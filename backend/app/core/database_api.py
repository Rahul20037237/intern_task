from dataclasses import dataclass, field

from sqlalchemy import Row, RowMapping

from backend.app.config import settings
from typing import Dict, Any, Sequence
import requests
from supabase import create_client,Client

@dataclass
class DocDatabase:
    bucket_name: str = field(default_factory=lambda: settings.BUCKET_NAME)
    supabase:Client=create_client(settings.SUPABASE_URL,settings.SUPABASE_SERVICE_ROLE_KEY.get_secret_value())

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



from typing import Type, TypeVar, List, Optional, Sequence, Union
from sqlmodel import SQLModel, select, Session, create_engine

T = TypeVar("T", bound=SQLModel)

class ApiDatabase:
    engine = create_engine(settings.DATABASE_URL, echo=True)

    def get_session(self) -> Session:
        return Session(self.engine)

    def create_tables(self) -> None:
        SQLModel.metadata.create_all(self.engine)

    def read_all(self, model: Type[T]) -> List[T]:
        with self.get_session() as session:
            statement = select(model)
            results = session.exec(statement)
            return results.all()

    def find_by_id(self, model: Type[T], ID: int) -> Optional[T]:
        with self.get_session() as session:
            return session.get(model, ID)

    def update(self, model: Type[T], ID: int, data: dict) -> Optional[T]:
        with self.get_session() as session:
            obj = session.get(model, ID)
            if not obj:
                return None
            for key, value in data.items():
                setattr(obj, key, value)
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj

    def delete(self, model: Type[T], ID: int) -> bool:
        with self.get_session() as session:
            obj = session.get(model, ID)
            if not obj:
                return False
            session.delete(obj)
            session.commit()
            return True

    def filter(self, model: Type[T], **filters) -> List[T]:
        try:
            with self.get_session() as session:
                statement = select(model)
                for attr, value in filters.items():
                    statement = statement.where(getattr(model, attr) == value)
                results = session.exec(statement)
                return results.all()
        except Exception as e:
            print(f"Error in filter method: {e}")
            return []

    def filter_and_delete(self, model: Type[T], **filters) -> int:
        try:
            with self.get_session() as session:
                statement = select(model)
                for attr, value in filters.items():
                    statement = statement.where(getattr(model, attr) == value)
                results = session.exec(statement).all()
                count = 0
                for obj in results:
                    session.delete(obj)
                    count += 1
                session.commit()
                return count
        except Exception as e:
            print(f"Error in filter_and_delete method: {e}")
            return 0
