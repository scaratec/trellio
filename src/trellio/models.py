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

class TrelloList(BaseModel):
    id: str
    name: str
    id_board: str = Field(alias="idBoard")
    closed: bool = False
    pos: float | int = 0

class TrelloCard(BaseModel):
    id: str
    name: str
    id_list: str = Field(alias="idList")
    id_board: Optional[str] = Field(default=None, alias="idBoard")
    description: Optional[str] = Field(default="", alias="desc")
    closed: bool = False
    url: Optional[str] = None
    pos: Optional[float | int | str] = None
    short_url: Optional[str] = Field(default=None, alias="shortUrl")
    due: Optional[str] = None
    due_complete: bool = Field(default=False, alias="dueComplete")
