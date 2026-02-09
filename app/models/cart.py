from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

# --- CABECERA DEL CARRITO (Uno por usuario) ---
class Cart(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True) # Un carrito por usuario
    
    # Relación con los items del carrito
    items: List["CartItem"] = Relationship(back_populates="cart")

# --- ITEMS DEL CARRITO (Productos dentro del carrito) ---
class CartItem(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cart_id: int = Field(foreign_key="cart.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int = Field(default=1)

    # Relación inversa
    cart: Cart = Relationship(back_populates="items")
    # Para acceder fácilmente al producto, aunque no lo guardamos en esta tabla
    # product: Product = Relationship(back_populates="cart_items") # Esto requeriría añadir 'cart_items' a Product model