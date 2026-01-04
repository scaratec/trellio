import httpx
from typing import List, Optional
from .models import TrelloMember, TrelloBoard

class TrellioClient:
    """
    An asynchronous client for the Trello API using httpx.
    
    This client handles authentication via API Key and Token and provides
    methods to interact with Trello resources like Members and Boards.
    """

    def __init__(self, api_key: str, token: str, base_url: str = "https://api.trello.com"):
        """
        Initialize the TrellioClient.

        Args:
            api_key (str): The Trello API Key.
            token (str): The Trello API Token.
            base_url (str, optional): The base URL of the Trello API. Defaults to "https://api.trello.com".
                                      Useful for testing against mock servers.
        """
        self.api_key = api_key
        self.token = token
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient()

    async def _request(self, method: str, path: str, **kwargs):
        """
        Internal method to make HTTP requests to the Trello API.
        
        Injects authentication parameters automatically.
        """
        params = kwargs.get("params", {})
        params["key"] = self.api_key
        params["token"] = self.token
        kwargs["params"] = params

        url = f"{self.base_url}{path}"
        response = await self._client.request(method, url, **kwargs)
        
        if response.status_code != 200:
            # Simple error handling for now
            raise Exception(f"Trello API error {response.status_code}: {response.text}")
        
        return response.json()

    async def get_me(self) -> TrelloMember:
        """
        Retrieve information about the authenticated user (member).
        """
        data = await self._request("GET", "/1/members/me")
        return TrelloMember(**data)

    async def list_boards(self) -> List[TrelloBoard]:
        """
        List all boards associated with the authenticated member.
        """
        data = await self._request("GET", "/1/members/me/boards")
        return [TrelloBoard(**board) for board in data]

    async def create_board(self, name: str, description: Optional[str] = None) -> TrelloBoard:
        """
        Create a new board.

        Args:
            name (str): The name of the new board.
            description (str, optional): The description of the board.
        """
        params = {"name": name}
        if description:
            params["desc"] = description
        
        data = await self._request("POST", "/1/boards", params=params)
        return TrelloBoard(**data)

    async def get_board(self, board_id: str) -> TrelloBoard:
        """
        Retrieve a specific board by its ID.
        """
        data = await self._request("GET", f"/1/boards/{board_id}")
        return TrelloBoard(**data)

    async def update_board(self, board_id: str, **kwargs) -> TrelloBoard:
        """
        Update a board's properties.

        Args:
            board_id (str): The ID of the board to update.
            **kwargs: Fields to update (e.g., name, desc, closed).
        """
        # Use query params for updates as well, common in Trello API
        data = await self._request("PUT", f"/1/boards/{board_id}", params=kwargs)
        return TrelloBoard(**data)

    async def delete_board(self, board_id: str):
        """
        Delete a board permanently.
        """
        await self._request("DELETE", f"/1/boards/{board_id}")

    async def close(self):
        """
        Close the underlying httpx client.
        """
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
