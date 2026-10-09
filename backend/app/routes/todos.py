from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Todo
from app.schemas import TodoCreate, TodoResponse, TodoUpdate

# 整个 router 都是管理接口，鉴权由 main.py 注册时统一挂上 require_admin
router = APIRouter(tags=["todos"])


@router.get("", response_model=list[TodoResponse])
def list_todos(db: Session = Depends(get_db)):
    """清单。没做完的排前面，勾掉之后自动沉到底部"""
    return db.query(Todo).order_by(Todo.done, Todo.id.desc()).all()


@router.post("", response_model=TodoResponse)
def create_todo(payload: TodoCreate, db: Session = Depends(get_db)):
    todo = Todo(text=payload.text)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@router.patch("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, payload: TodoUpdate, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="条目不存在")

    # 只改传过来的字段。PATCH 是部分更新 ——
    # 写 todo.text = payload.text 会让「只改完成状态」的请求把文字清空
    if payload.text is not None:
        todo.text = payload.text
    if payload.done is not None:
        todo.done = payload.done

    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="条目不存在")

    db.delete(todo)
    db.commit()
    return {"message": "已删除"}
