from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

# --- CATEGORÍAS ---
class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    description: Optional[str] = None

    # Relación: El "back_populates" debe coincidir con el nombre del atributo en Product
    products: List["Product"] = Relationship(back_populates="category")

class CategoryCreate(SQLModel):
    name: str
    description: Optional[str] = None


# --- PRODUCTOS ---
class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    sku: str = Field(unique=True, index=True)
    price: float = Field(default=0.0)
    stock: int = Field(default=0)
    
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")

    category: Optional[Category] = Relationship(back_populates="products")

class ProductCreate(SQLModel):
    name: str
    sku: str
    price: float
    stock: int
    category_id: int