from typing import TypedDict, List, Dict
from langchain_core.documents import Document

class QueryState(TypedDict):
    query: str
    results: List[Document]
    answers: List[Dict]
    themes: Dict[str, List[str]]