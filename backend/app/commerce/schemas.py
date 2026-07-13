from uuid import UUID

from pydantic import BaseModel


class CartItemCreate(BaseModel):
    variant_id: UUID
    quantity: int


class CartItemUpdate(BaseModel):
    quantity: int
