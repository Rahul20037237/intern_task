from dataclasses import dataclass
from  fastapi import  APIRouter,File,UploadFile
@dataclass
class DocumentApi:
     Doc_db:str
     router: APIRouter
     prefix:str="/api/documents"
     tags=["Documents"]
     def __post_init__(self):
          self.router=APIRouter(prefix=self.prefix)
     def add_routes(self):
          tags=self.tags