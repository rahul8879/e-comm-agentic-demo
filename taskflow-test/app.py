"""FastAPI application for TaskFlow."""

from math import ceil

from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

DEFAULT_PAGE: int = 1
DEFAULT_PAGE_SIZE: int = 10
MIN_PAGE: int = 1
MIN_PAGE_SIZE: int = 1
MAX_PAGE_SIZE: int = 100


class Task(BaseModel):
    """Represents a task in the TaskFlow system."""

    id: int = Field(..., description="Unique task identifier.")
    title: str = Field(..., description="Human-readable task title.")
    completed: bool = Field(..., description="Whether the task is completed.")


class TaskListResponse(BaseModel):
    """Paginated list of tasks."""

    items: list[Task] = Field(..., description="Tasks for the current page.")
    page: int = Field(..., description="Current page number.")
    page_size: int = Field(..., description="Number of tasks per page.")
    total_items: int = Field(..., description="Total number of tasks available.")
    total_pages: int = Field(..., description="Total number of pages available.")


app = FastAPI(title="TaskFlow API")

TASKS: list[Task] = [
    Task(id=1, title="Set up project repository", completed=True),
    Task(id=2, title="Define task data model", completed=True),
    Task(id=3, title="Implement task listing endpoint", completed=False),
    Task(id=4, title="Add pagination support", completed=False),
    Task(id=5, title="Write API documentation", completed=False),
]


@app.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    page: int = Query(DEFAULT_PAGE, ge=MIN_PAGE, description="Page number."),
    page_size: int = Query(
        DEFAULT_PAGE_SIZE,
        ge=MIN_PAGE_SIZE,
        le=MAX_PAGE_SIZE,
        description="Number of tasks to return per page.",
    ),
) -> TaskListResponse:
    """Return a paginated list of tasks."""

    total_items: int = len(TASKS)
    total_pages: int = ceil(total_items / page_size) if total_items else 0
    start_index: int = (page - 1) * page_size
    end_index: int = start_index + page_size
    paginated_tasks: list[Task] = TASKS[start_index:end_index]

    return TaskListResponse(
        items=paginated_tasks,
        page=page,
        page_size=page_size,
        total_items=total_items,
        total_pages=total_pages,
    )
