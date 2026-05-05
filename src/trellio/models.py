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

class TrelloLabel(BaseModel):
    id: str
    name: str
    color: Optional[str] = None
    id_board: str = Field(alias="idBoard")


class TrelloCheckItem(BaseModel):
    id: str
    name: str
    state: str = "incomplete"
    pos: Optional[float | int | str] = None


class TrelloChecklist(BaseModel):
    id: str
    name: str
    id_card: str = Field(alias="idCard")
    check_items: List["TrelloCheckItem"] = Field(default_factory=list, alias="checkItems")


class TrelloComment(BaseModel):
    id: str
    text: str
    date: Optional[str] = None
    id_member_creator: Optional[str] = Field(default=None, alias="idMemberCreator")


class TrelloAttachment(BaseModel):
    id: str
    name: str
    url: str
    bytes: Optional[int] = None
    date: Optional[str] = None
    id_member: Optional[str] = Field(default=None, alias="idMember")


class TrelloWebhook(BaseModel):
    id: str
    description: Optional[str] = None
    callback_url: str = Field(alias="callbackURL")
    id_model: str = Field(alias="idModel")
    active: bool = True


class TrelloSearchResult(BaseModel):
    boards: List["TrelloBoard"] = Field(default_factory=list)
    cards: List["TrelloCard"] = Field(default_factory=list)


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
    id_labels: List[str] = Field(default_factory=list, alias="idLabels")
    id_members: List[str] = Field(default_factory=list, alias="idMembers")
    id_checklists: List[str] = Field(default_factory=list, alias="idChecklists")
    due: Optional[str] = None
    due_complete: bool = Field(default=False, alias="dueComplete")
    date_last_activity: Optional[str] = Field(default=None, alias="dateLastActivity")
    badges: Optional[dict] = None
    labels: Optional[list] = None
