from typing import Optional, List
from pydantic import BaseModel, Field

class TrelloMember(BaseModel):
    id: str
    username: str
    full_name: str = Field(alias="fullName")
    email: Optional[str] = None
    url: Optional[str] = None

class TrelloBoard(BaseModel):
    id: str
    name: str
    description: Optional[str] = Field(default="", alias="desc")
    closed: bool = False
    url: Optional[str] = None
