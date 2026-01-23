from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class Category(SQLModel, table=True):
    """Representa las categorías de productos (ej. Electrónica, Alimentos)"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None

    # Relación inversa: una categoría tiene muchos productos
    products: List["Product"] = Relationship(back_populates="category")

class Product(SQLModel, table=True):
    """Representa un artículo del inventario"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    sku: str = Field(unique=True, index=True) 
    description: Optional[str] = None
    price: float = Field(default=0.0)
    stock: int = Field(default=0)
    
    # Llave foránea
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")
    
    # Relación: Un producto pertenece a una categoría
    category: Optional[Category] = Relationship(back_populates="products")