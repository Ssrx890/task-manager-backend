from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.models.orders import Order, OrderItem
from app.models.inventory import Product
from app.api.v1.deps import get_current_user
from app.models.user import User
from typing import List

router = APIRouter(prefix="/orders", tags=["Ventas"])

@router.post("/")
def create_order(
    items_data: List[dict], # Formato: [{"product_id": 1, "quantity": 2}]
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """
    Proceso de Venta Profesional:
    1. Crea la cabecera del pedido.
    2. Valida stock de cada producto.
    3. Descuenta stock y crea el detalle.
    4. Si algo falla, hace Rollback automático.
    """
    try:
        new_order = Order(user_id=current_user.id)
        session.add(new_order)
        session.flush() # Para obtener el ID de la orden sin confirmar cambios aún

        running_total = 0.0

        for item in items_data:
            product = session.get(Product, item["product_id"])
            
            if not product:
                raise HTTPException(status_code=404, detail=f"Producto ID {item['product_id']} no existe")
            
            if product.stock < item["quantity"]:
                raise HTTPException(status_code=400, detail=f"Stock insuficiente para {product.name}")

            # Lógica financiera y de stock
            subtotal = product.price * item["quantity"]
            running_total += subtotal
            product.stock -= item["quantity"] # Descuento de inventario

            order_detail = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                quantity=item["quantity"],
                unit_price=product.price
            )
            session.add(order_detail)
            session.add(product)

        new_order.total = running_total
        session.commit()
        session.refresh(new_order)
        
        return {"status": "Venta exitosa", "order_id": new_order.id, "total": new_order.total}

    except Exception as e:
        session.rollback() # Seguridad total: si algo falla, no se toca el stock
        raise e