from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models.inventory import Product, Category
from app.api.v1.deps import get_current_user
from app.models.user import User
from typing import List


router = APIRouter(prefix="/inventory", tags=["Inventario"])

@router.post("/products", response_model=Product)
def create_product(
    product: Product, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """Solo el ADMIN puede crear o editar productos"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Operación no permitida para vendedores")
    
    session.add(product)
    session.commit()
    session.refresh(product)
    return product

@router.get("/products", response_model=List[Product])
def list_products(session: Session = Depends(get_session)):
    """Cualquier usuario logueado puede ver el stock"""
    return session.exec(select(Product)).all()

@router.post("/categories", response_model=Category)
def create_category(category: Category, session: Session = Depends(get_session)):
    session.add(category)
    session.commit()
    session.refresh(category)
    return category