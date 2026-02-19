from typing import Optional
from sqlmodel import SQLModel


class OrderItemInput(SQLModel):
    """Schema para items al crear una orden manual"""
    product_id: int
    quantity: int


class ProductUpdate(SQLModel):
    """Schema para actualización parcial de productos"""
    name: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    category_id: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryUpdate(SQLModel):
    """Schema para actualización parcial de categorías"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
