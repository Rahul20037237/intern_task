from fastapi import FastAPI, APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlmodel import SQLModel
from typing import TypeVar, Dict, List, Type
from io import StringIO
import csv

T = TypeVar("T", bound=SQLModel)

class MainApi:
    def __init__(self, prefix: str, model: Type[T], tags: str):
        self.router = APIRouter(prefix=prefix)
        self.model = model
        self.tags = tags
        self.db: Dict[int, T] = {}

    def add_routes(self):
        model = self.model
        tags = self.tags
        db = self.db

        @self.router.post("/", tags=[tags], response_model=model)
        def create(item: model):  # type: ignore
            if item.id not in db:
                db[item.id] = item
                return item
            else:
                raise HTTPException(status_code=400, detail="Already exists")

        @self.router.get("/all", tags=[tags], response_model=List[model])
        def list_all():
            return list(db.values())

        @self.router.get("/{id}", tags=[tags], response_model=model)
        def get(id: int):
            if id not in db:
                raise HTTPException(status_code=404, detail="Not found")
            return db[id]

        @self.router.put("/{id}", tags=[tags], response_model=model)
        def update(id: int, item: model):  # type: ignore
            if id not in db:
                raise HTTPException(status_code=404, detail="Item not found")
            db[id] = item
            return item

        @self.router.delete("/{id}", tags=[tags])
        def delete(id: int):
            if id not in db:
                raise HTTPException(status_code=404, detail="Item not found")
            del db[id]
            return {"message": "Item deleted"}

        @self.router.get("/search", tags=[tags], response_model=List[model])
        def search(q: str = ""):
            return [item for item in db.values() if q.lower() in str(item).lower()]


        @self.router.get("/export", tags=[tags])
        def export_csv():
            if not db:
                raise HTTPException(status_code=404, detail="No data to export")

            output = StringIO()
            sample = next(iter(db.values()))
            writer = csv.DictWriter(output, fieldnames=sample.model_dump().keys())
            writer.writeheader()
            for item in db.values():
                writer.writerow(item.model_dump())
            output.seek(0)
            return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=data.csv"})