# Changelog

All notable changes to this project will be documented in this
file.

The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.8.0] - 2026-05-05

### Added
- `list_check_items(checklist_id)` method on `TrellioClient`,
  mapping to `GET /1/checklists/{id}/checkItems`. Returns
  `List[TrelloCheckItem]` with `id`, `name`, `state`, `pos`
  per item. Enables reading existing check item IDs, which
  is required for `update_check_item` and `delete_check_item`
  after session boundaries.
- `pos` field (`Optional[float | int | str]`) on
  `TrelloCheckItem` model, matching the Trello API response
- Mock server route for the `/checkItems` endpoint, including
  `pos` persistence with top/bottom/numeric support
- 5 BDD scenarios covering happy path (with varianz), empty
  list, state round-trip, position ordering, and 404 error

[1.8.0]: https://github.com/scaratec/trellio/compare/v1.7.0...v1.8.0

## [1.2.1] - 2026-04-14

### Fixed
- `add_comment`, `list_comments`, and `update_comment` now
  correctly parse Trello Action objects (extract `data.text`
  and `memberCreator.id` instead of expecting flat top-level
  fields), fixing Pydantic validation errors against the real
  Trello API
- Mock server comment endpoints now return realistic Action
  object structures matching the real Trello API response
  format

[1.2.1]: https://github.com/scaratec/trellio/compare/v1.2.0...v1.2.1

## [1.0.0] - 2026-04-08

### Added

#### Infrastructure
- Async HTTP client built on `httpx` with full type hints
- Pydantic v2 models for all Trello resource types
- `TrelloAPIError` typed exception with `status_code` and
  `message` fields
- Retry with exponential backoff for transient errors
  (429, 500, 502, 503, 504), configurable via `max_retries`,
  `initial_delay`, `backoff_factor`
- `Retry-After` header support on 429 responses
- Configurable request timeout (default 30s)
- Cursor-based pagination: `list_boards(limit, since)` and
  `list_all_boards(page_size)` async generator
- Structured logging via `trellio` logger (DEBUG for requests,
  WARNING for retries, ERROR for failures)
- Async context manager support for connection lifecycle

#### Resources (38 client methods, 11 models)
- **Authentication:** `get_me`
- **Boards:** `list_boards`, `list_all_boards`, `create_board`,
  `get_board`, `update_board`, `delete_board`
- **Lists:** `list_lists`, `create_list`
- **Cards:** `list_cards`, `create_card`, `get_card`,
  `update_card`, `delete_card`
- **Labels:** `list_board_labels`, `create_label`,
  `update_label`, `delete_label`
- **Checklists:** `list_card_checklists`, `create_checklist`,
  `get_checklist`, `delete_checklist`, `create_check_item`,
  `update_check_item`, `delete_check_item`
- **Comments:** `add_comment`, `list_comments`,
  `update_comment`, `delete_comment`
- **Members:** `list_board_members`, `get_member`
- **Attachments:** `list_attachments`, `create_attachment`,
  `delete_attachment`
- **Webhooks:** `create_webhook`, `list_webhooks`,
  `get_webhook`, `update_webhook`, `delete_webhook`
- **Search:** `search` with `TrelloSearchResult`

#### Testing
- BDD test suite: 16 features, 117 scenarios, 826 steps
- Custom mock server simulating Trello API with in-memory
  state, JSON error responses, forced error/delay mechanisms
- Scenario Outlines with data variants for anti-hardcoding
- Independent persistence validation (re-GET after writes)
- Error path coverage: input validation, auth failures,
  404s, rate limiting (429), server errors (500)
- Layer-by-layer failure path enumeration (ADR 003)
- Mock validation against py-trello reference library

#### Documentation
- Architecture Decision Records (ADR 001-003)
- README with API reference table and usage examples
- pyproject.toml for pip-installability from GitHub

### Changed
- License changed from MIT to GPL-3.0-or-later

[1.0.0]: https://github.com/scaratec/trellio/releases/tag/v1.0.0
