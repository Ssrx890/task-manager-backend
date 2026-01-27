from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.api.v1.deps import get_current_user
from app.models.user import User
from app.models.inventory import Product, ProductCreate, Category, CategoryCreate

router = APIRouter(prefix="/inventory", tags=["Inventario"])

# --- ENDPOINTS DE CATEGORÍAS ---

@router.post("/categories", response_model=Category)
def create_category(category_data: CategoryCreate, session: Session = Depends(get_session)):
    existing_category = session.exec(
        select(Category).where(Category.name == category_data.name)
    ).first()
    
    if existing_category:
        raise HTTPException(
            status_code=400, 
            detail=f"La categoría '{category_data.name}' ya existe."
        )

    db_category = Category.model_validate(category_data)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category

@router.get("/categories", response_model=List[Category])
def list_categories(session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()


# --- ENDPOINTS DE PRODUCTOS ---

@router.post("/products", response_model=Product)
def create_product(
    product_data: ProductCreate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Crea un producto. Solo accesible por ADMIN."""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permisos para gestionar productos"
        )
    
    # Validamos que la categoría exista antes de crear el producto
    category = session.get(Category, product_data.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="La categoría especificada no existe")

    # Creamos el objeto de base de datos a partir del esquema de entrada
    db_product = Product.model_validate(product_data)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product

@router.get("/products", response_model=List[Product])
def list_products(session: Session = Depends(get_session)):
    return session.exec(select(Product)).all()