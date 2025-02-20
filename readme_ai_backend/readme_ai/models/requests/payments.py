from pydantic import BaseModel
from typing import List


class ProductItem(BaseModel):
    price_id: str
    quantity: int = 1


class CheckoutRequest(BaseModel):
    items: List[ProductItem]
