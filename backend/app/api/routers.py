from  fastapi import  FastAPI
from .endpoints.query_api import MainApi
from ..models.api_models import *
app = FastAPI()

query_router=MainApi(prefix="/api/query",model=QueryAPI,tags="query")
query_router.add_routes()

document_router=MainApi(prefix="/api/document",model=DocumentAPI,tags="document")
document_router.add_routes()

theme_router=MainApi(prefix="/api/theme",model=ThemeAPI,tags="theme")
theme_router.add_routes()


app.include_router(query_router.router)
app.include_router(document_router.router)
app.include_router(theme_router.router)
