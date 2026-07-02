"""Task API routes."""

from math import ceil
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Task

DEFAULT_PAGE: int = 1
DEFAULT_PAGE_SIZE: int = 10
MIN_PAGE: int = 1
MIN_PAGE_SIZE: int = 1
MAX_PAGE_SIZE: int = 100

router = APIRouter()


@router.get("/tasks")
async def get_tasks(
    page: int = Query(DEFAULT_PAGE, ge=MIN_PAGE),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=MIN_PAGE_SIZE, le=MAX_PAGE_SIZE),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return a paginated list of tasks."""

    total_items: int = db.query(Task).count()
    total_pages: int = ceil(total_items / page_size) if total_items else 0
    offset: int = (page - 1) * page_size
    tasks: list[Task] = db.query(Task).offset(offset).limit(page_size).all()

    return {
        "items": tasks,
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
    }


@router.post("/tasks")
def create_task(title: str, db: Session = Depends(get_db)) -> Task:
    """Create a new task."""

    task = Task(title=title)
    db.add(task)
    db.commit()
    return task
