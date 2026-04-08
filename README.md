# Trellio - Async Trello API Client for Python

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

**Trellio** is a production-ready, asynchronous Python client for the Trello API, built on `httpx` and `pydantic`. Designed for use in long-running services like MCP servers, it provides retry with backoff, request timeouts, structured logging, and full CRUD coverage across 10 Trello resource types.

## Features

### Infrastructure
- **Async I/O** -- built on `httpx.AsyncClient`, non-blocking
- **Retry with exponential backoff** -- automatic retry on 429/5xx, respects `Retry-After` header, configurable `max_retries`, `initial_delay`, `backoff_factor`
- **Request timeout** -- configurable per-client, raises `TrelloAPIError` on timeout
- **Pagination** -- `list_boards(limit, since)` for single pages, `list_all_boards(page_size)` async generator for auto-pagination
- **Structured logging** -- `trellio` logger with DEBUG (every request), WARNING (retries), ERROR (failures)
- **Typed exceptions** -- `TrelloAPIError(status_code, message)` for all API errors
- **Pydantic models** -- type-safe response objects with alias support for Trello's camelCase API

### Resources (38 client methods)

| Resource    | Methods |
|-------------|---------|
| Auth        | `get_me` |
| Boards      | `list_boards`, `list_all_boards`, `create_board`, `get_board`, `update_board`, `delete_board` |
| Lists       | `list_lists`, `create_list` |
| Cards       | `list_cards`, `create_card`, `get_card`, `update_card`, `delete_card` |
| Labels      | `list_board_labels`, `create_label`, `update_label`, `delete_label` |
| Checklists  | `list_card_checklists`, `create_checklist`, `get_checklist`, `delete_checklist`, `create_check_item`, `update_check_item`, `delete_check_item` |
| Comments    | `add_comment`, `list_comments`, `update_comment`, `delete_comment` |
| Members     | `list_board_members`, `get_member` |
| Attachments | `list_attachments`, `create_attachment`, `delete_attachment` |
| Webhooks    | `create_webhook`, `list_webhooks`, `get_webhook`, `update_webhook`, `delete_webhook` |
| Search      | `search` |

### Models

`TrelloMember`, `TrelloBoard`, `TrelloList`, `TrelloCard`, `TrelloLabel`, `TrelloChecklist`, `TrelloCheckItem`, `TrelloComment`, `TrelloAttachment`, `TrelloWebhook`, `TrelloSearchResult`

## Quick Start

```python
import asyncio
from trellio import TrellioClient

async def main():
    async with TrellioClient(
        api_key="your_key",
        token="your_token",
        max_retries=3,
        timeout=30.0,
    ) as client:
        boards = await client.list_boards()
        for board in boards:
            print(board.name)

        results = await client.search("project")
        for card in results.cards:
            print(card.name)

asyncio.run(main())
```

## MCP Server Usage

```python
from trellio import TrellioClient, TrelloAPIError

client = TrellioClient(
    api_key=os.environ["TRELLO_API_KEY"],
    token=os.environ["TRELLO_TOKEN"],
    max_retries=3,
    initial_delay=1.0,
    timeout=30.0,
)

# Use in MCP tool handlers:
async def handle_create_card(list_id: str, name: str):
    try:
        card = await client.create_card(list_id, name)
        return {"id": card.id, "name": card.name}
    except TrelloAPIError as e:
        return {"error": e.message, "status": e.status_code}
```

## Philosophy: BDD & Single Source of Truth

This project follows strict **Behavior-Driven Development (BDD)** where Gherkin feature files are the **Single Source of Truth** for business logic. All implementation is derivative of the specifications.

## Test Coverage

The BDD suite covers **16 features, 117 scenarios, 826 steps**:

| Feature        | Scenarios |
|----------------|-----------|
| Authentication | 6         |
| Boards         | 11        |
| Cards          | 13        |
| Lists          | 6         |
| Labels         | 9         |
| Checklists     | 13        |
| Comments       | 9         |
| Members        | 4         |
| Attachments    | 7         |
| Webhooks       | 13        |
| Retry          | 7         |
| Pagination     | 4         |
| Connection     | 2         |
| Timeout        | 2         |
| Search         | 4         |
| Logging        | 3         |
| **Total**      | **117**   |

## Development Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Run BDD suite
PYTHONPATH=src python -m behave

# Run mock validation
PYTHONPATH=src pytest tests/validation/
```

## Architecture Decisions

| ADR | Title | Status |
|-----|-------|--------|
| [001](docs/adr/001-custom-mock-server.md) | Custom Mock Server and Validation Strategy | Accepted |
| [002](docs/adr/002-mock-server-selection.md) | Mock Strategy: Custom Python vs. MockServer | Accepted |
| [003](docs/adr/003-failure-path-enumeration.md) | Failure Path Enumeration | Accepted |

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
