import httpx
from typing import List, Optional, Union
from .models import TrelloMember, TrelloBoard, TrelloList, TrelloCard
from .errors import TrelloAPIError


class TrellioClient:

    def __init__(self, api_key: str, token: str, base_url: str = "https://api.trello.com"):
        self.api_key = api_key
        self.token = token
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient()

    async def _authenticated_request(self, method: str, path: str, **kwargs):
        params = kwargs.get("params", {})
        params["key"] = self.api_key
        params["token"] = self.token
        kwargs["params"] = params

        url = f"{self.base_url}{path}"
        response = await self._client.request(method, url, **kwargs)

        if response.status_code != 200:
            raise TrelloAPIError(response.status_code, response.text)

        return response.json()

    async def get_me(self) -> TrelloMember:
        data = await self._authenticated_request("GET", "/1/members/me")
        return TrelloMember(**data)

    async def list_boards(self) -> List[TrelloBoard]:
        data = await self._authenticated_request("GET", "/1/members/me/boards")
        return [TrelloBoard(**board) for board in data]

    async def create_board(self, name: str, description: Optional[str] = None) -> TrelloBoard:
        params = {"name": name}
        if description:
            params["desc"] = description
        data = await self._authenticated_request("POST", "/1/boards", params=params)
        return TrelloBoard(**data)

    async def get_board(self, board_id: str) -> TrelloBoard:
        data = await self._authenticated_request("GET", f"/1/boards/{board_id}")
        return TrelloBoard(**data)

    async def update_board(self, board_id: str, **kwargs) -> TrelloBoard:
        data = await self._authenticated_request("PUT", f"/1/boards/{board_id}", params=kwargs)
        return TrelloBoard(**data)

    async def delete_board(self, board_id: str):
        await self._authenticated_request("DELETE", f"/1/boards/{board_id}")

    async def create_list(self, board_id: str, name: str, pos: Union[str, float] = "top") -> TrelloList:
        params = {"name": name, "idBoard": board_id, "pos": pos}
        data = await self._authenticated_request("POST", "/1/lists", params=params)
        return TrelloList(**data)

    async def create_card(self, list_id: str, name: str, desc: Optional[str] = None, pos: Union[str, float] = "top") -> TrelloCard:
        params = {"name": name, "idList": list_id, "pos": pos}
        if desc:
            params["desc"] = desc
        data = await self._authenticated_request("POST", "/1/cards", params=params)
        return TrelloCard(**data)

    async def get_card(self, card_id: str) -> TrelloCard:
        data = await self._authenticated_request("GET", f"/1/cards/{card_id}")
        return TrelloCard(**data)

    async def update_card(self, card_id: str, **kwargs) -> TrelloCard:
        data = await self._authenticated_request("PUT", f"/1/cards/{card_id}", params=kwargs)
        return TrelloCard(**data)

    async def delete_card(self, card_id: str):
        await self._authenticated_request("DELETE", f"/1/cards/{card_id}")

    async def close(self):
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
