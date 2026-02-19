from typing import Optional, List
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship


class Order(SQLModel, table=True):
    """Cabecera de la Factura (Snapshot Legal)"""
    id: Optional[int] = Field(default=None, primary_key=True)
    invoice_number: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    subtotal: float = Field(default=0.0)
    tax_amount: float = Field(default=0.0)
    total: float = Field(default=0.0)

    status: str = Field(default="COMPLETED")
    payment_type: str = Field(default="CASH")
    user_id: int = Field(foreign_key="user.id")

    items: List["OrderItem"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    """Detalle de la Factura (Snapshot del Producto)"""
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")

    product_name_snapshot: str
    unit_price_snapshot: float

    quantity: int
    subtotal: float

    order: Order = Relationship(back_populates="items")