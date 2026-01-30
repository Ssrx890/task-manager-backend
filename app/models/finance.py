from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class Debt(SQLModel, table=True):
    """Representa el saldo pendiente de una venta a crédito"""
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", unique=True)
    
    customer_name: str = Field(index=True) 
    
    total_amount: float = Field(default=0.0)
    balance: float = Field(default=0.0)
    status: str = Field(default="OPEN")

    payments: List["Payment"] = Relationship(back_populates="debt")

class Payment(SQLModel, table=True):
    """Registro de abonos individuales a una deuda"""
    id: Optional[int] = Field(default=None, primary_key=True)
    debt_id: int = Field(foreign_key="debt.id")
    amount: float = Field(default=0.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    debt: Debt = Relationship(back_populates="payments")

class PaymentCreate(SQLModel):
    """Esquema para recibir un nuevo pago"""
    amount: float