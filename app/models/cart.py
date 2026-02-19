from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

# --- ITEMS DEL CARRITO (Productos dentro del carrito) ---
class CartItemBase(SQLModel):
    product_id: int
    quantity: int = Field(default=1)

class CartItem(CartItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cart_id: int = Field(foreign_key="cart.id")

    # Relación inversa
    cart: "Cart" = Relationship(back_populates="items")

class CartItemRead(CartItemBase):
    id: int
    cart_id: int

# --- CABECERA DEL CARRITO (Uno por usuario) ---
class CartBase(SQLModel):
    user_id: int = Field(foreign_key="user.id", unique=True)

class Cart(CartBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Relación con los items del carrito
    items: List[CartItem] = Relationship(back_populates="cart")

class CartRead(CartBase):
    id: int
    items: List[CartItemRead] = []