from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, func
from app.database import get_session
from app.api.deps import get_current_user
from app.models.user import User
from app.models.inventory import Product
from app.models.orders import Order, OrderItem
from app.models.finance import Debt
from app.models.cart import Cart

router = APIRouter(prefix="/orders", tags=["Ventas y Facturación"])

# --- CONSTANTE DE IMPUESTOS (Nivel Arquitecto) ---
IVA_RATE = 0.19 

@router.post("/from_cart")
def create_invoice_from_cart(
    payment_type: str = Query("CASH", description="CASH o CREDIT"),
    customer_name: Optional[str] = Query(None, description="Nombre del cliente para crédito"),
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """
    PROCESO DE FACTURACIÓN PROFESIONAL:
    1. Valida el carrito del usuario.
    2. Genera número de factura correlativo.
    3. Captura Snapshots (nombre/precio) para que la factura sea inmutable.
    4. Calcula impuestos y totales.
    5. Emite warnings si el stock llega a cero.
    6. Gestiona la deuda si es crédito.
    """
    
    # 1. Obtener y validar carrito
    cart = session.exec(select(Cart).where(Cart.user_id == current_user.id)).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="El carrito está vacío.")

    if payment_type == "CREDIT" and not customer_name:
        raise HTTPException(status_code=400, detail="El nombre del cliente es obligatorio para ventas a crédito.")

    try:
        # 2. Generar número de factura (FAC-1, FAC-2...)
        last_order_id = session.exec(select(func.max(Order.id))).one() or 0
        invoice_no = f"FAC-{last_order_id + 1}"

        new_order = Order(
            user_id=current_user.id,
            invoice_number=invoice_no,
            payment_type=payment_type,
            status="COMPLETED"
        )
        session.add(new_order)
        session.flush() # Reservamos el ID de la orden

        running_subtotal = 0.0
        stock_warnings = []

        # 3. Procesar ítems del carrito
        for cart_item in cart.items:
            product = session.get(Product, cart_item.product_id)
            
            # Validaciones de seguridad
            if not product or not product.is_active:
                session.rollback()
                raise HTTPException(status_code=404, detail=f"Producto {cart_item.product_id} ya no está disponible.")
            
            if product.stock < cart_item.quantity:
                session.rollback()
                raise HTTPException(status_code=400, detail=f"Stock insuficiente para {product.name}.")

            # Lógica de Snapshot (Inmutabilidad)
            item_total_price = product.price * cart_item.quantity
            running_subtotal += item_total_price
            
            # Descuento de stock real
            product.stock -= cart_item.quantity

            # --- REQUERIMIENTO: Alerta de Stock a Cero ---
            if product.stock == 0:
                stock_warnings.append({
                    "product_id": product.id,
                    "name": product.name,
                    "msg": "¡STOCK AGOTADO! ¿Desea reponerlo o eliminarlo del catálogo?"
                })

            # Crear detalle de factura (OrderItem)
            invoice_item = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                product_name_snapshot=product.name,  # Guardamos el nombre actual
                unit_price_snapshot=product.price,    # Guardamos el precio actual
                quantity=cart_item.quantity,
                subtotal=item_total_price
            )
            session.add(invoice_item)
            session.add(product)

        # 4. Cálculos Financieros
        new_order.subtotal = running_subtotal
        new_order.tax_amount = running_subtotal * IVA_RATE
        new_order.total = new_order.subtotal + new_order.tax_amount

        # 5. Gestión de Deuda (Crédito)
        if payment_type == "CREDIT":
            new_debt = Debt(
                order_id=new_order.id,
                customer_name=customer_name,
                total_amount=new_order.total,
                balance=new_order.total
            )
            session.add(new_debt)

        # 6. Limpieza: Vaciar carrito tras la venta exitosa
        for item in cart.items:
            session.delete(item)

        session.commit()
        session.refresh(new_order)

        return {
            "status": "Venta exitosa",
            "factura": new_order.invoice_number,
            "total_pagado": new_order.total,
            "cliente": customer_name or "Consumidor Final",
            "warnings": stock_warnings # Aquí el Frontend recibe las alertas de stock 0
        }

    except Exception as e:
        session.rollback()
        raise e

@router.get("/{order_id}/invoice")
def get_invoice_detail(order_id: int, session: Session = Depends(get_session)):
    """Devuelve la factura completa. Los nombres de productos son inmutables."""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    return order