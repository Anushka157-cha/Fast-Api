from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlalchemy.orm import Session

from database import get_db
from models import TaskDB, UserDB
from schemas import TaskCreate, TaskUpdate, TaskResponse
from security import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    new_task = TaskDB(**data.model_dump(), owner_id=current_user.id)
    try:
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return new_task
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create task"
        )

@router.get("", response_model=list[TaskResponse])
def get_tasks(
    completed: bool | None = None,
    search: str | None = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    query = db.query(TaskDB).filter(TaskDB.owner_id == current_user.id)

    if completed is not None:
        query = query.filter(TaskDB.completed == completed)

    if search is not None:
        query = query.filter(TaskDB.title.ilike(f"%{search}%"))

    return query.offset(skip).limit(limit).all()

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int = Path(..., ge=1, description="Task ID must be a positive integer"),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    task = db.query(TaskDB).filter(
        TaskDB.id == task_id,
        TaskDB.owner_id == current_user.id
    ).first()

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return task

@router.put("/{task_id}", response_model=TaskResponse)
def replace_task(
    task_id: int = Path(..., ge=1, description="Task ID must be a positive integer"),
    data: TaskCreate = ...,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    task = db.query(TaskDB).filter(
        TaskDB.id == task_id,
        TaskDB.owner_id == current_user.id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    task.title = data.title
    task.completed = data.completed

    try:
        db.commit()
        db.refresh(task)
        return task
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update task"
        )

@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int = Path(..., ge=1, description="Task ID must be a positive integer"),
    data: TaskUpdate = ...,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    task = db.query(TaskDB).filter(
        TaskDB.id == task_id,
        TaskDB.owner_id == current_user.id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    updates = data.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided to update"
        )

    for key, value in updates.items():
        setattr(task, key, value)

    try:
        db.commit()
        db.refresh(task)
        return task
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not update task"
        )

@router.delete("/{task_id}")
def delete_task(
    task_id: int = Path(..., ge=1, description="Task ID must be a positive integer"),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    task = db.query(TaskDB).filter(
        TaskDB.id == task_id,
        TaskDB.owner_id == current_user.id
    ).first()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    try:
        db.delete(task)
        db.commit()
        return {
            "message": "Task deleted successfully",
            "task_id": task_id
        }
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not delete task"
        )
