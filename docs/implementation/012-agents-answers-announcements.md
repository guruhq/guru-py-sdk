# Iteration 012 — Agents + Answers + Announcements

**Status**: Complete
**Date**: 2026-04-13

## Goal

Add AgentResource (Knowledge Agents), AnswerResource (AI Q&A), and AnnouncementResource (card broadcasts). These are the final three resources in the guru-cli public API surface.

## Scope

### AgentResource (10 methods)

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | /assistants | List all agents | `list[KnowledgeAgent]` |
| GET | /assistants/{id} | Get by ID | `KnowledgeAgent` |
| — | resolve(id_or_name) | UUID → get, name → list + match | `KnowledgeAgent` |
| POST | /assistants | Create agent | `KnowledgeAgent` |
| PUT | /assistants/{id} | Update agent | `KnowledgeAgent` |
| DELETE | /assistants/{id} | Delete agent | None |
| GET | /assistants/{id}/groups | List group access | `list[KnowledgeAgentAccess]` |
| POST | /assistants/{id}/groups | Add group access | `KnowledgeAgentAccess` |
| PUT | /assistants/{id}/groups/{gid} | Update group role | `KnowledgeAgentAccess` |
| DELETE | /assistants/{id}/groups/{gid} | Remove group access | None |

### AnswerResource (2 methods)

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| POST | /answers | Full answer with sources | `Answer` |
| POST | /answers/minimal | Lighter answer | `Answer` |

### AnnouncementResource (3 methods)

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | /alerts | List announcements | `list[KnowledgeAlertDelegated]` |
| POST | /alerts | Broadcast a card | `KnowledgeAlertDelegated` |
| GET | /announcements/{id}/stats/summary | Read stats | `AnnouncementInsightSummary` |

## Implementation

### New Files
- `src/guru_sdk/resources/agents.py` — AgentResource (10 public methods)
- `src/guru_sdk/resources/answers.py` — AnswerResource (2 public methods)
- `src/guru_sdk/resources/announcements.py` — AnnouncementResource (3 public methods)
- `tests/resources/test_agents.py` — 31 tests
- `tests/resources/test_answers.py` — 9 tests
- `tests/resources/test_announcements.py` — 11 tests

### Modified Files
- `src/guru_sdk/client.py` — Added `self.agents`, `self.announcements`, `self.answers`
- `src/guru_sdk/__init__.py` — Added resource exports
- `src/guru_sdk/models/__init__.py` — Added model exports (AnnouncementInsightSummary, AnnouncementUser, KnowledgeAlert, KnowledgeAlertDelegated)

## Design Decisions

1. **No flattening**: Unlike guru-cli which flattens nested objects to IDs/names, the py-sdk uses Pydantic models as-is. Callers access nested data via `agent.created_by.email` instead of a flat `created_by_email` field.

2. **Name resolution on AgentResource**: First resource in the py-sdk with a `resolve()` method. Uses `is_uuid()` to decide between direct `get()` and `list()` + case-insensitive match. Raises `NotFoundError` with available names.

3. **API naming**: API uses "assistants" and "alerts" — SDK uses "agents" and "announcements" to match Guru product terminology.

4. **Announcement groups format**: `POST /alerts` expects `groups: [{id: "..."}]` — not a flat list of IDs. The SDK handles this mapping internally.

## Test Summary

- 51 new tests (535 total)
- Agents: 31 tests (list 2, get 3, resolve 4, create 4, update 3, delete 2, list_groups 3, add_group 4, update_group 3, remove_group 3)
- Answers: 9 tests (ask 6, ask_minimal 3)
- Announcements: 11 tests (list 3, create 5, stats 2)

## Enum/Model Gotchas

- `AgentType`: `DEEP_AGENT`, `LEGACY` (not `STANDARD`)
- `Role2` (group access role): `ADMIN`, `EXPERT`, `VIEWER` (not `MEMBER`)
- `Document.document_type`: Required field (not optional)
- `Card.preferred_phrase`: Required field (not optional)
- `AnnouncementUser`: Flat structure — user fields at top level, not nested under `user`
- `RoleModel.id`: `UUID` type, not plain `str`

## Quality Gates

- ruff: ✅ clean
- pytest: ✅ 535 passed
- mypy: ⏭ verify on Mac
