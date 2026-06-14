from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Item
from app.schemas import ItemCreate, ItemResponse

router = APIRouter(tags=["items"])


@router.get("/items", response_model=list[ItemResponse])
def get_items(db: Session = Depends(get_db)):
    return db.query(Item).all()


@router.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return {"error": "Item not found"}
    return item


@router.post("/items", response_model=ItemResponse)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)):
    item = Item(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
