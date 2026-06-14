from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    price: float = 0.0
    description: str = ""


class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    description: str

    model_config = {"from_attributes": True}
