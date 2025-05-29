
from sqlmodel import  Field,SQLModel,Relationship
from typing import  List,Optional

class QueryAPI(SQLModel):
    Query_ID:str=Field(...,regex=r'^Query [0-9]{1,2}$')
    Query:str

class ThemeAPI(SQLModel, table=True):
    Theme_ID: str = Field(default=None, primary_key=True, regex=r'^Theme [0-9]{1,2}$')
    Theme_name: str = Field(..., regex=r'^Theme [0-9]{1,2}[\w\W\s\S]*$')

    documents: List["DocumentAPI"] = Relationship(back_populates="theme")


class DocumentAPI(SQLModel, table=True):
    Document_ID: str = Field(default=None, primary_key=True, regex=r'^DOC[0-9]{1,2}$')
    Document_name: str = Field(..., regex=r'^Theme [0-9]{1,2}[\w\W\s\S]*$')
    answer: str
    citation: str = Field(nullable=False)
    Query_relation: str = Field(..., regex=r'^Query [0-9]{1,2}$')

    # Foreign key to Theme table
    Theme_relation: str = Field(foreign_key="ThemeAPI.Theme_ID", regex=r'^Theme [0-9]{1,2}$')

    # Reverse link to theme
    theme: Optional[ThemeAPI] = Relationship(back_populates="documents")



