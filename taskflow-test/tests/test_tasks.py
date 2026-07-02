"""Tests for the task routes."""

import importlib
import sys
import types
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class FakeTask:
    """Simple task object for route tests."""

    def __init__(self, task_id: int, title: str) -> None:
        """Store task attributes used by the response serializer."""

        self.id = task_id
        self.title = title


class FakeQuery:
    """Minimal query object that supports pagination methods."""

    def __init__(self, items: list[FakeTask]) -> None:
        """Initialize the query state."""

        self._items = items
        self._offset = 0
        self._limit: int | None = None

    def count(self) -> int:
        """Return the total number of tasks."""

        return len(self._items)

    def offset(self, value: int) -> "FakeQuery":
        """Store the pagination offset."""

        self._offset = value
        return self

    def limit(self, value: int) -> "FakeQuery":
        """Store the pagination limit."""

        self._limit = value
        return self

    def all(self) -> list[FakeTask]:
        """Return the paginated task slice."""

        end_index: int | None = None if self._limit is None else self._offset + self._limit
        return self._items[self._offset:end_index]


class FakeSession:
    """Minimal session object with a SQLAlchemy-like query API."""

    def __init__(self, items: list[FakeTask]) -> None:
        """Initialize session state."""

        self._items = items

    def query(self, _: Any) -> FakeQuery:
        """Return a query object for the requested model."""

        return FakeQuery(self._items)


@pytest.fixture
def tasks_module(monkeypatch: pytest.MonkeyPatch) -> types.ModuleType:
    """Import the tasks module with stubbed dependencies."""

    database_module = types.ModuleType("database")
    database_module.get_db = lambda: None
    models_module = types.ModuleType("models")
    models_module.Task = FakeTask
    sqlalchemy_module = types.ModuleType("sqlalchemy")
    sqlalchemy_orm_module = types.ModuleType("sqlalchemy.orm")
    sqlalchemy_orm_module.Session = object
    sqlalchemy_module.orm = sqlalchemy_orm_module

    monkeypatch.setitem(sys.modules, "database", database_module)
    monkeypatch.setitem(sys.modules, "models", models_module)
    monkeypatch.setitem(sys.modules, "sqlalchemy", sqlalchemy_module)
    monkeypatch.setitem(sys.modules, "sqlalchemy.orm", sqlalchemy_orm_module)
    sys.modules.pop("tasks", None)

    return importlib.import_module("tasks")


def create_client(tasks_module: types.ModuleType, items: list[FakeTask]) -> TestClient:
    """Build a test client with dependency overrides."""

    app = FastAPI()
    app.include_router(tasks_module.router)
    app.dependency_overrides[tasks_module.get_db] = lambda: FakeSession(items)
    return TestClient(app)


def test_get_tasks_happy_path(tasks_module: types.ModuleType) -> None:
    """Return the default first page of tasks."""

    client = create_client(
        tasks_module,
        [
            FakeTask(1, "First task"),
            FakeTask(2, "Second task"),
            FakeTask(3, "Third task"),
        ],
    )

    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {"id": 1, "title": "First task"},
            {"id": 2, "title": "Second task"},
            {"id": 3, "title": "Third task"},
        ],
        "page": 1,
        "page_size": 10,
        "total_items": 3,
        "total_pages": 1,
    }


def test_get_tasks_applies_pagination(tasks_module: types.ModuleType) -> None:
    """Return the requested page slice and pagination metadata."""

    client = create_client(
        tasks_module,
        [
            FakeTask(1, "Task 1"),
            FakeTask(2, "Task 2"),
            FakeTask(3, "Task 3"),
            FakeTask(4, "Task 4"),
            FakeTask(5, "Task 5"),
        ],
    )

    response = client.get("/tasks", params={"page": 2, "page_size": 2})

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {"id": 3, "title": "Task 3"},
            {"id": 4, "title": "Task 4"},
        ],
        "page": 2,
        "page_size": 2,
        "total_items": 5,
        "total_pages": 3,
    }


def test_get_tasks_returns_empty_list(tasks_module: types.ModuleType) -> None:
    """Return empty pagination metadata when no tasks exist."""

    client = create_client(tasks_module, [])

    response = client.get("/tasks")

    assert response.status_code == 200
    assert response.json() == {
        "items": [],
        "page": 1,
        "page_size": 10,
        "total_items": 0,
        "total_pages": 0,
    }


@pytest.mark.parametrize(
    ("params", "invalid_field"),
    [
        ({"page": 0}, "page"),
        ({"page_size": 0}, "page_size"),
        ({"page_size": 101}, "page_size"),
    ],
)
def test_get_tasks_rejects_invalid_params(
    tasks_module: types.ModuleType,
    params: dict[str, int],
    invalid_field: str,
) -> None:
    """Reject invalid pagination query parameters."""

    client = create_client(tasks_module, [FakeTask(1, "Task 1")])

    response = client.get("/tasks", params=params)

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert any(entry["loc"][-1] == invalid_field for entry in detail)
