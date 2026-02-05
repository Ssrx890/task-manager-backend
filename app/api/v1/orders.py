from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from app.database import get_session
from app.api.deps import get_current_user
from app.models.user import User
from app.models.inventory import Product
from app.models.orders import Order, OrderItem
from app.models.finance import Debt


router = APIRouter(prefix="/orders", tags=["Ventas"])

@router.post("/")
def create_order(
    items_data: List[dict], 
    payment_type: str = Query("CASH", description="CASH o CREDIT"),
    customer_name: Optional[str] = Query(None, description="Nombre si es crédito"),
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    # Validación de Arquitecto: Si es crédito, el nombre es OBLIGATORIO
    if payment_type == "CREDIT" and not customer_name:
        raise HTTPException(
            status_code=400, 
            detail="Para ventas a crédito, el nombre del cliente es obligatorio."
        )

    try:
        new_order = Order(user_id=current_user.id)
        session.add(new_order)
        session.flush() 

        running_total = 0.0
        for item in items_data:
            product = session.get(Product, item["product_id"])
            if not product or product.stock < item["quantity"]:
                raise HTTPException(status_code=400, detail="Stock insuficiente")

            subtotal = product.price * item["quantity"]
            running_total += subtotal
            product.stock -= item["quantity"]

            detail = OrderItem(
                order_id=new_order.id, product_id=product.id,
                quantity=item["quantity"], unit_price=product.price
            )
            session.add(detail)
            session.add(product)

        new_order.total = running_total
        
        # Lógica de Deuda con Nombre
        if payment_type == "CREDIT":
            new_debt = Debt(
                order_id=new_order.id,
                customer_name=customer_name, # Guardamos el nombre
                total_amount=running_total,
                balance=running_total
            )
            session.add(new_debt)

        session.commit()
        return {"status": "Venta exitosa", "cliente": customer_name, "total": running_total}

    except Exception as e:
        session.rollback()
        raise e