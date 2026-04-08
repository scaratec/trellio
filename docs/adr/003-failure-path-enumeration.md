# ADR 003: Failure Path Enumeration

- **Status:** Accepted
- **Date:** 2026-04-08
- **Context:**
  BDD Guidelines v1.8.0, Guideline 4.5, requires a formal tabular enumeration
  of all failure paths across all layers, with a count per layer and a coverage
  status column. This document serves as that persistent artifact.

- **Decision:**
  We maintain this table as the single source of truth for failure path coverage.
  Every new failure scenario added to a `.feature` file must be reflected here.

## Failure Path Enumeration

| #  | Layer                  | Failure Path                            | HTTP | Feature File           | Scenario                                              | Covered |
|----|------------------------|-----------------------------------------|------|------------------------|-------------------------------------------------------|---------|
| 1  | Input Validation       | Board created without name              | 400  | boards.feature         | Fail to create a board without a name                 | Yes     |
| 2  | Input Validation       | Card created without name               | 400  | cards.feature          | Fail to create a card without a name                  | Yes     |
| 3  | Input Validation       | Card created in non-existent list       | 400  | cards.feature          | Fail to create a card in a non-existent list          | Yes     |
| 4  | Input Validation       | List created without name               | 400  | lists.feature          | Fail to create a list without a name                  | Yes     |
| 5  | Input Validation       | List created without board ID           | 400  | lists.feature          | Fail to create a list without a board ID              | Yes     |
| 6  | Authentication         | Invalid API key                         | 401  | authentication.feature | Failed Authentication with invalid key                | Yes     |
| 7  | Authentication         | Missing API key                         | 401  | authentication.feature | Failed Authentication with missing API Key            | Yes     |
| 8  | Authentication         | Empty API key                           | 401  | authentication.feature | Failed Authentication with empty API Key              | Yes     |
| 9  | Authentication         | Empty API token                         | 401  | authentication.feature | Failed Authentication with empty Token                | Yes     |
| 10 | External Communication | Server returns 429 on board creation    | 429  | boards.feature         | Server returns 429 rate limit error on board creation | Yes     |
| 11 | External Communication | Server returns 500 on board retrieval   | 500  | boards.feature         | Server returns 500 internal error on board retrieval  | Yes     |
| 12 | External Communication | Server returns 429 on card creation     | 429  | cards.feature          | Server returns 429 rate limit error on card creation  | Yes     |
| 13 | External Communication | Server returns 500 on card retrieval    | 500  | cards.feature          | Server returns 500 internal error on card retrieval   | Yes     |
| 14 | External Communication | Server returns 429 on list creation     | 429  | lists.feature          | Server returns 429 rate limit error on list creation  | Yes     |
| 15 | Response Processing    | Board not found (GET)                   | 404  | boards.feature         | Fail to get a non-existent board                      | Yes     |
| 16 | Response Processing    | Board not found (PUT)                   | 404  | boards.feature         | Fail to update a non-existent board                   | Yes     |
| 17 | Response Processing    | Board not found (DELETE)                | 404  | boards.feature         | Fail to delete a non-existent board                   | Yes     |
| 18 | Response Processing    | Card not found (GET)                    | 404  | cards.feature          | Fail to get a non-existent card                       | Yes     |
| 19 | Response Processing    | Card not found (PUT)                    | 404  | cards.feature          | Fail to update a non-existent card                    | Yes     |
| 20 | Response Processing    | Card not found (DELETE)                 | 404  | cards.feature          | Fail to delete a non-existent card                    | Yes     |
| 21 | Data Integrity         | Created board retrievable by ID         | 200  | boards.feature         | Create a new board (Outline, re-GET verification)     | Yes     |
| 22 | Data Integrity         | Updated board retrievable with new name | 200  | boards.feature         | Update a board (Outline, re-GET verification)         | Yes     |
| 23 | Data Integrity         | Deleted board no longer retrievable     | 404  | boards.feature         | Delete a board (re-GET -> 404)                        | Yes     |
| 24 | Data Integrity         | Created card retrievable by ID          | 200  | cards.feature          | Create a new card (Outline, re-GET verification)      | Yes     |
| 25 | Data Integrity         | Updated card retrievable with new name  | 200  | cards.feature          | Update a card (Outline, re-GET verification)          | Yes     |
| 26 | Data Integrity         | Updated card desc retrievable           | 200  | cards.feature          | Update card description (Outline, re-GET verification)| Yes     |
| 27 | Data Integrity         | Deleted card no longer retrievable      | 404  | cards.feature          | Delete a card (re-GET -> 404)                         | Yes     |

## Summary by Layer

| Layer                  | Total | Covered |
|------------------------|-------|---------|
| Input Validation       | 5     | 5       |
| Authentication         | 4     | 4       |
| External Communication | 5     | 5       |
| Response Processing    | 6     | 6       |
| Data Integrity         | 7     | 7       |
| **Total**              | **27**| **27**  |

- **Consequences:**
  All identified failure paths are covered by BDD scenarios. This table must be
  updated whenever new failure scenarios are added or existing ones change.
