from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.api.deps import get_current_user
from app.models.user import User
from app.models.inventory import Product # Necesario para validar productos
from app.models.cart import Cart, CartItem

router = APIRouter(prefix="/cart", tags=["Carrito"])

def get_user_cart(user_id: int, session: Session) -> Cart:
    """Función auxiliar para obtener o crear el carrito de un usuario."""
    cart = session.exec(select(Cart).where(Cart.user_id == user_id)).first()
    if not cart:
        cart = Cart(user_id=user_id)
        session.add(cart)
        session.commit()
        session.refresh(cart)
    return cart

@router.get("/", response_model=Cart)
def get_cart(
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """Obtiene el carrito actual del usuario logueado."""
    return get_user_cart(current_user.id, session)

@router.post("/items", response_model=Cart)
def add_item_to_cart(
    product_id: int, 
    quantity: int = 1,
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """Añade o actualiza la cantidad de un producto en el carrito."""
    cart = get_user_cart(current_user.id, session)
    product = session.get(Product, product_id)

    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    if quantity <= 0:
        raise HTTPException(status_code=400, detail="La cantidad debe ser mayor que cero")
    if quantity > product.stock:
        raise HTTPException(status_code=400, detail=f"Solo quedan {product.stock} unidades de {product.name}")

    cart_item = session.exec(
        select(CartItem)
        .where(CartItem.cart_id == cart.id)
        .where(CartItem.product_id == product_id)
    ).first()

    if cart_item:
        cart_item.quantity = quantity
    else:
        cart_item = CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity)
    
    session.add(cart_item)
    session.commit()
    session.refresh(cart) # Refrescar para que incluya los items actualizados
    return cart

@router.delete("/items/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item_from_cart(
    product_id: int, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """Elimina un producto del carrito."""
    cart = get_user_cart(current_user.id, session)
    cart_item = session.exec(
        select(CartItem)
        .where(CartItem.cart_id == cart.id)
        .where(CartItem.product_id == product_id)
    ).first()

    if not cart_item:
        raise HTTPException(status_code=404, detail="Producto no encontrado en el carrito")
    
    session.delete(cart_item)
    session.commit()
    return

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """Vacía completamente el carrito del usuario."""
    cart = get_user_cart(current_user.id, session)
    for item in cart.items:
        session.delete(item)
    session.commit()
    return