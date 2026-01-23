from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class Order(SQLModel, table=True):
    """Cabecera de la venta"""
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    total: float = Field(default=0.0)
    status: str = Field(default="COMPLETED") # PENDING, COMPLETED, CANCELLED
    payment_type: str = Field(default="CASH") # CASH, DEBT 

    user_id: int = Field(foreign_key="user.id")
    
    # Un pedido tiene muchos items
    items: List["OrderItem"] = Relationship(back_populates="order")

class OrderItem(SQLModel, table=True):
    """Detalle individual de cada producto en una venta"""
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    
    quantity: int
    unit_price: float # Importante: guardamos el precio al momento de la venta

    order: Order = Relationship(back_populates="items")