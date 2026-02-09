from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, func
from app.database import get_session
from app.api.deps import get_current_user
from app.models.user import User
from app.models.inventory import Product
from app.models.orders import Order, OrderItem
from app.models.finance import Debt
from app.models.cart import Cart, CartItem

router = APIRouter(prefix="/orders", tags=["Ventas y Facturación"])

# --- FUNCIÓN AUXILIAR PARA CÁLCULOS ---
def calculate_invoice_totals(items_total: float, tax_rate: float = 0.19):
    """Calcula subtotal, impuestos y total final"""
    subtotal = items_total
    tax = subtotal * tax_rate
    total = subtotal + tax
    return subtotal, tax, total

# --- 1. CREAR ORDEN MANUAL (Para ventas rápidas sin carrito) ---
@router.post("/", summary="Crear Orden con ítems manuales", response_model=dict)
def create_order(
    items_data: List[dict], 
    payment_type: str = Query("CASH", description="CASH o CREDIT"),
    customer_name: Optional[str] = Query(None, description="Nombre si es crédito"),
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    # Validación: Si es crédito, el nombre es OBLIGATORIO
    if payment_type == "CREDIT" and not customer_name:
        raise HTTPException(
            status_code=400, 
            detail="Para ventas a crédito, el nombre del cliente es obligatorio."
        )

    try:
        # Generar número de factura (FAC-X)
        last_id = session.exec(select(func.max(Order.id))).one() or 0
        invoice_no = f"FAC-{last_id + 1}"

        new_order = Order(
            user_id=current_user.id,
            invoice_number=invoice_no,
            payment_type=payment_type
        )
        session.add(new_order)
        session.flush() # Para obtener ID de la orden

        running_items_total = 0.0

        for item in items_data:
            product = session.get(Product, item["product_id"])
            if not product or product.stock < item["quantity"]:
                session.rollback()
                raise HTTPException(status_code=400, detail=f"Stock insuficiente para ID {item['product_id']}")

            # SNAPSHOT: Capturamos datos actuales para la factura
            item_subtotal = product.price * item["quantity"]
            running_items_total += item_subtotal
            
            product.stock -= item["quantity"]

            order_detail = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                product_name_snapshot=product.name, # Nombre capturado
                unit_price_snapshot=product.price, # Precio capturado
                quantity=item["quantity"],
                subtotal=item_subtotal
            )
            session.add(order_detail)
            session.add(product)

        # Totales con impuestos
        sub, tax, total = calculate_invoice_totals(running_items_total)
        new_order.subtotal = sub
        new_order.tax_amount = tax
        new_order.total = total
        
        # Lógica de Deuda
        if payment_type == "CREDIT":
            new_debt = Debt(
                order_id=new_order.id,
                customer_name=customer_name,
                total_amount=total,
                balance=total
            )
            session.add(new_debt)

        session.commit()
        session.refresh(new_order)
        return {
            "status": "Venta exitosa", 
            "factura": new_order.invoice_number,
            "total": total,
            "cliente": customer_name or "Consumidor Final"
        }

    except Exception as e:
        session.rollback()
        raise e

# --- 2. CREAR ORDEN DESDE EL CARRITO ---
@router.post("/from_cart", summary="Crear Orden desde el Carrito")
def create_order_from_cart(
    payment_type: str = Query("CASH", description="CASH o CREDIT"),
    customer_name: Optional[str] = Query(None, description="Nombre si es crédito"),
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    # Validar si el carrito existe y tiene items
    cart = session.exec(select(Cart).where(Cart.user_id == current_user.id)).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="El carrito está vacío.")

    if payment_type == "CREDIT" and not customer_name:
        raise HTTPException(status_code=400, detail="Nombre del cliente obligatorio para crédito.")

    try:
        # Generar nro factura
        last_id = session.exec(select(func.max(Order.id))).one() or 0
        invoice_no = f"FAC-{last_id + 1}"

        new_order = Order(
            user_id=current_user.id,
            invoice_number=invoice_no,
            payment_type=payment_type
        )
        session.add(new_order)
        session.flush()

        running_items_total = 0.0

        for cart_item in cart.items:
            product = session.get(Product, cart_item.product_id)
            if not product or product.stock < cart_item.quantity:
                session.rollback()
                raise HTTPException(status_code=400, detail=f"Stock insuficiente para {product.name}")

            item_subtotal = product.price * cart_item.quantity
            running_items_total += item_subtotal
            product.stock -= cart_item.quantity

            # Snapshot del item
            detail = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                product_name_snapshot=product.name,
                unit_price_snapshot=product.price,
                quantity=cart_item.quantity,
                subtotal=item_subtotal
            )
            session.add(detail)
            session.add(product)

        # Totales
        sub, tax, total = calculate_invoice_totals(running_items_total)
        new_order.subtotal = sub
        new_order.tax_amount = tax
        new_order.total = total

        if payment_type == "CREDIT":
            new_debt = Debt(
                order_id=new_order.id,
                customer_name=customer_name,
                total_amount=total,
                balance=total
            )
            session.add(new_debt)

        # Vaciar carrito tras éxito
        for c_item in cart.items:
            session.delete(c_item)

        session.commit()
        session.refresh(new_order)
        return {
            "status": "Venta realizada desde carrito", 
            "factura": new_order.invoice_number, 
            "total": total
        }

    except Exception as e:
        session.rollback()
        raise e

# --- 3. VER DETALLE DE FACTURA (Para el Frontend) ---
@router.get("/{order_id}/invoice")
def get_invoice_detail(order_id: int, session: Session = Depends(get_session)):
    """Obtiene toda la información de una factura incluyendo snapshots"""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Factura no encontrada")
    
    # SQLModel cargará automáticamente los items gracias a Relationship
    return order