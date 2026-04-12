import asyncio
import logging
import time
import httpx
from typing import AsyncGenerator, List, Optional, Union
from .models import (
    TrelloMember, TrelloBoard, TrelloList, TrelloCard,
    TrelloLabel, TrelloChecklist, TrelloCheckItem,
    TrelloComment, TrelloAttachment, TrelloWebhook,
    TrelloSearchResult,
)
from .errors import TrelloAPIError

logger = logging.getLogger("trellio")

RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


class TrellioClient:

    def __init__(self, api_key: str, token: str, base_url: str = "https://api.trello.com",
                 max_retries: int = 3, initial_delay: float = 1.0, backoff_factor: float = 2.0,
                 timeout: float = 30.0):
        self.api_key = api_key
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.backoff_factor = backoff_factor
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    async def _authenticated_request(self, method: str, path: str, **kwargs):
        params = kwargs.get("params", {})
        params["key"] = self.api_key
        params["token"] = self.token
        kwargs["params"] = params

        url = f"{self.base_url}{path}"
        last_error = None

        for attempt in range(self.max_retries + 1):
            start = time.monotonic()
            try:
                response = await self._client.request(method, url, **kwargs)
            except httpx.TimeoutException:
                logger.error("%s %s timed out after %.0fms", method, path, (time.monotonic() - start) * 1000)
                raise TrelloAPIError(0, "Request timed out")

            duration_ms = (time.monotonic() - start) * 1000
            logger.debug("%s %s %d (%.0fms)", method, path, response.status_code, duration_ms)

            if response.status_code == 200:
                return response.json()

            if response.status_code not in RETRYABLE_STATUS_CODES or attempt == self.max_retries:
                logger.error("Request failed: %s %s %d", method, path, response.status_code)
                raise TrelloAPIError(response.status_code, response.text)

            retry_after = response.headers.get("Retry-After")
            if retry_after:
                delay = float(retry_after)
            else:
                delay = self.initial_delay * (self.backoff_factor ** attempt)
            logger.warning("Retry %d/%d for %s %s (status %d, delay %.1fs)",
                           attempt + 1, self.max_retries, method, path, response.status_code, delay)
            last_error = TrelloAPIError(response.status_code, response.text)
            if delay > 0:
                await asyncio.sleep(delay)

        raise last_error

    async def get_me(self) -> TrelloMember:
        data = await self._authenticated_request("GET", "/1/members/me")
        return TrelloMember(**data)

    async def list_boards(self, limit: Optional[int] = None, since: Optional[str] = None) -> List[TrelloBoard]:
        params = {}
        if limit is not None:
            params["limit"] = limit
        if since is not None:
            params["since"] = since
        data = await self._authenticated_request("GET", "/1/members/me/boards", params=params)
        return [TrelloBoard(**board) for board in data]

    async def list_all_boards(self, page_size: int = 50) -> AsyncGenerator[TrelloBoard, None]:
        cursor = None
        while True:
            boards = await self.list_boards(limit=page_size, since=cursor)
            if not boards:
                break
            for board in boards:
                yield board
            if len(boards) < page_size:
                break
            cursor = boards[-1].id

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

    async def list_lists(self, board_id: str) -> List[TrelloList]:
        data = await self._authenticated_request("GET", f"/1/boards/{board_id}/lists")
        return [TrelloList(**lst) for lst in data]

    async def list_cards(self, list_id: str) -> List[TrelloCard]:
        data = await self._authenticated_request("GET", f"/1/lists/{list_id}/cards")
        return [TrelloCard(**card) for card in data]

    async def create_card(self, list_id: str, name: str, desc: Optional[str] = None, pos: Union[str, float] = "top", idLabels: Optional[str] = None) -> TrelloCard:
        params = {"name": name, "idList": list_id, "pos": pos}
        if desc:
            params["desc"] = desc
        if idLabels:
            params["idLabels"] = idLabels
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

    async def add_label_to_card(self, card_id: str, label_id: str):
        await self._authenticated_request("POST", f"/1/cards/{card_id}/idLabels", data={"value": label_id})

    async def remove_label_from_card(self, card_id: str, label_id: str):
        await self._authenticated_request("DELETE", f"/1/cards/{card_id}/idLabels/{label_id}")

    # --- Labels ---

    async def list_board_labels(self, board_id: str) -> List[TrelloLabel]:
        data = await self._authenticated_request("GET", f"/1/boards/{board_id}/labels")
        return [TrelloLabel(**label) for label in data]

    async def create_label(self, name: str, color: str, board_id: str) -> TrelloLabel:
        params = {"name": name, "color": color, "idBoard": board_id}
        data = await self._authenticated_request("POST", "/1/labels", params=params)
        return TrelloLabel(**data)

    async def update_label(self, label_id: str, **kwargs) -> TrelloLabel:
        data = await self._authenticated_request("PUT", f"/1/labels/{label_id}", params=kwargs)
        return TrelloLabel(**data)

    async def delete_label(self, label_id: str):
        await self._authenticated_request("DELETE", f"/1/labels/{label_id}")

    # --- Checklists ---

    async def list_card_checklists(self, card_id: str) -> List[TrelloChecklist]:
        data = await self._authenticated_request("GET", f"/1/cards/{card_id}/checklists")
        return [TrelloChecklist(**cl) for cl in data]

    async def create_checklist(self, card_id: str, name: str) -> TrelloChecklist:
        params = {"idCard": card_id, "name": name}
        data = await self._authenticated_request("POST", "/1/checklists", params=params)
        return TrelloChecklist(**data)

    async def get_checklist(self, checklist_id: str) -> TrelloChecklist:
        data = await self._authenticated_request("GET", f"/1/checklists/{checklist_id}")
        return TrelloChecklist(**data)

    async def delete_checklist(self, checklist_id: str):
        await self._authenticated_request("DELETE", f"/1/checklists/{checklist_id}")

    async def create_check_item(self, checklist_id: str, name: str) -> TrelloCheckItem:
        data = await self._authenticated_request("POST", f"/1/checklists/{checklist_id}/checkItems", params={"name": name})
        return TrelloCheckItem(**data)

    async def update_check_item(self, card_id: str, check_item_id: str, state: str) -> TrelloCheckItem:
        data = await self._authenticated_request("PUT", f"/1/cards/{card_id}/checkItem/{check_item_id}", params={"state": state})
        return TrelloCheckItem(**data)

    async def delete_check_item(self, checklist_id: str, check_item_id: str):
        await self._authenticated_request("DELETE", f"/1/checklists/{checklist_id}/checkItems/{check_item_id}")

    # --- Comments ---

    async def add_comment(self, card_id: str, text: str) -> TrelloComment:
        data = await self._authenticated_request("POST", f"/1/cards/{card_id}/actions/comments", params={"text": text})
        return TrelloComment(**data)

    async def list_comments(self, card_id: str) -> List[TrelloComment]:
        data = await self._authenticated_request("GET", f"/1/cards/{card_id}/actions", params={"filter": "commentCard"})
        return [TrelloComment(**comment) for comment in data]

    async def update_comment(self, comment_id: str, text: str) -> TrelloComment:
        data = await self._authenticated_request("PUT", f"/1/actions/{comment_id}", params={"text": text})
        return TrelloComment(**data)

    async def delete_comment(self, comment_id: str):
        await self._authenticated_request("DELETE", f"/1/actions/{comment_id}")

    # --- Members ---

    async def list_board_members(self, board_id: str) -> List[TrelloMember]:
        data = await self._authenticated_request("GET", f"/1/boards/{board_id}/members")
        return [TrelloMember(**member) for member in data]

    async def get_member(self, member_id: str) -> TrelloMember:
        data = await self._authenticated_request("GET", f"/1/members/{member_id}")
        return TrelloMember(**data)

    # --- Attachments ---

    async def list_attachments(self, card_id: str) -> List[TrelloAttachment]:
        data = await self._authenticated_request("GET", f"/1/cards/{card_id}/attachments")
        return [TrelloAttachment(**att) for att in data]

    async def create_attachment(self, card_id: str, url: str, name: Optional[str] = None) -> TrelloAttachment:
        params = {"url": url}
        if name:
            params["name"] = name
        data = await self._authenticated_request("POST", f"/1/cards/{card_id}/attachments", params=params)
        return TrelloAttachment(**data)

    async def delete_attachment(self, card_id: str, attachment_id: str):
        await self._authenticated_request("DELETE", f"/1/cards/{card_id}/attachments/{attachment_id}")

    # --- Webhooks ---

    async def create_webhook(self, callback_url: str, id_model: str, description: Optional[str] = None) -> TrelloWebhook:
        params = {"callbackURL": callback_url, "idModel": id_model}
        if description:
            params["description"] = description
        data = await self._authenticated_request("POST", "/1/webhooks", params=params)
        return TrelloWebhook(**data)

    async def list_webhooks(self) -> List[TrelloWebhook]:
        data = await self._authenticated_request("GET", "/1/webhooks")
        return [TrelloWebhook(**wh) for wh in data]

    async def get_webhook(self, webhook_id: str) -> TrelloWebhook:
        data = await self._authenticated_request("GET", f"/1/webhooks/{webhook_id}")
        return TrelloWebhook(**data)

    async def update_webhook(self, webhook_id: str, **kwargs) -> TrelloWebhook:
        data = await self._authenticated_request("PUT", f"/1/webhooks/{webhook_id}", params=kwargs)
        return TrelloWebhook(**data)

    async def delete_webhook(self, webhook_id: str):
        await self._authenticated_request("DELETE", f"/1/webhooks/{webhook_id}")

    # --- Search ---

    async def search(self, query: str, model_types: Optional[str] = None, limit: int = 10) -> TrelloSearchResult:
        params = {"query": query, "cards_limit": limit, "boards_limit": limit}
        if model_types:
            params["modelTypes"] = model_types
        data = await self._authenticated_request("GET", "/1/search", params=params)
        boards = [TrelloBoard(**b) for b in data.get("boards", [])]
        cards = [TrelloCard(**c) for c in data.get("cards", [])]
        return TrelloSearchResult(boards=boards, cards=cards)

    async def close(self):
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
