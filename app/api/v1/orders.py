from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, func
from app.database import get_session
from app.api.deps import get_current_user, get_admin_user
from app.models.user import User
from app.models.inventory import Product
from app.models.orders import Order, OrderItem
from app.models.finance import Debt
from app.models.cart import Cart
from app.models.schemas import OrderItemInput

router = APIRouter(prefix="/orders", tags=["Ventas y Facturación"])


def _calculate_invoice_totals(items_total: float, tax_rate: float = 0.19):
    """Calcula subtotal, impuestos y total final."""
    tax = items_total * tax_rate
    total = items_total + tax
    return items_total, tax, total


def _generate_invoice_number(session: Session) -> str:
    """Genera un número de factura correlativo."""
    last_id = session.exec(select(func.max(Order.id))).one() or 0
    return f"FAC-{last_id + 1}"


# --- 1. CREAR ORDEN MANUAL ---
@router.post("/", summary="Crear orden con ítems manuales", response_model=dict)
def create_order(
    items_data: List[OrderItemInput],
    payment_type: str = Query("CASH", description="CASH o CREDIT"),
    customer_name: Optional[str] = Query(None, description="Nombre si es crédito"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if payment_type == "CREDIT" and not customer_name:
        raise HTTPException(
            status_code=400,
            detail="Para ventas a crédito, el nombre del cliente es obligatorio.",
        )

    try:
        new_order = Order(
            user_id=current_user.id,
            invoice_number=_generate_invoice_number(session),
            payment_type=payment_type,
        )
        session.add(new_order)
        session.flush()

        running_items_total = 0.0

        for item in items_data:
            product = session.get(Product, item.product_id)
            if not product or not product.is_active:
                session.rollback()
                raise HTTPException(status_code=404, detail=f"Producto {item.product_id} no disponible")
            if product.stock < item.quantity:
                session.rollback()
                raise HTTPException(status_code=400, detail=f"Stock insuficiente para {product.name}")

            item_subtotal = product.price * item.quantity
            running_items_total += item_subtotal
            product.stock -= item.quantity

            order_detail = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                product_name_snapshot=product.name,
                unit_price_snapshot=product.price,
                quantity=item.quantity,
                subtotal=item_subtotal,
            )
            session.add(order_detail)
            session.add(product)

        sub, tax, total = _calculate_invoice_totals(running_items_total)
        new_order.subtotal = sub
        new_order.tax_amount = tax
        new_order.total = total

        if payment_type == "CREDIT":
            new_debt = Debt(
                order_id=new_order.id,
                customer_name=customer_name,
                total_amount=total,
                balance=total,
            )
            session.add(new_debt)

        session.commit()
        session.refresh(new_order)
        return {
            "status": "Venta exitosa",
            "factura": new_order.invoice_number,
            "total": total,
            "cliente": customer_name or "Consumidor Final",
        }

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# --- 2. CREAR ORDEN DESDE EL CARRITO ---
@router.post("/from_cart", summary="Crear orden desde el carrito")
def create_order_from_cart(
    payment_type: str = Query("CASH", description="CASH o CREDIT"),
    customer_name: Optional[str] = Query(None, description="Nombre si es crédito"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    cart = session.exec(select(Cart).where(Cart.user_id == current_user.id)).first()
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="El carrito está vacío.")

    if payment_type == "CREDIT" and not customer_name:
        raise HTTPException(status_code=400, detail="Nombre del cliente obligatorio para crédito.")

    try:
        new_order = Order(
            user_id=current_user.id,
            invoice_number=_generate_invoice_number(session),
            payment_type=payment_type,
        )
        session.add(new_order)
        session.flush()

        running_items_total = 0.0
        stock_warnings = []

        for cart_item in cart.items:
            product = session.get(Product, cart_item.product_id)
            if not product or not product.is_active:
                session.rollback()
                raise HTTPException(status_code=404, detail=f"Producto {cart_item.product_id} ya no disponible")
            if product.stock < cart_item.quantity:
                session.rollback()
                raise HTTPException(status_code=400, detail=f"Stock insuficiente para {product.name}")

            item_subtotal = product.price * cart_item.quantity
            running_items_total += item_subtotal
            product.stock -= cart_item.quantity

            if product.stock == 0:
                stock_warnings.append({
                    "product_id": product.id,
                    "name": product.name,
                    "msg": "¡STOCK AGOTADO!",
                })

            detail = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                product_name_snapshot=product.name,
                unit_price_snapshot=product.price,
                quantity=cart_item.quantity,
                subtotal=item_subtotal,
            )
            session.add(detail)
            session.add(product)

        sub, tax, total = _calculate_invoice_totals(running_items_total)
        new_order.subtotal = sub
        new_order.tax_amount = tax
        new_order.total = total

        if payment_type == "CREDIT":
            new_debt = Debt(
                order_id=new_order.id,
                customer_name=customer_name,
                total_amount=total,
                balance=total,
            )
            session.add(new_debt)

        for c_item in cart.items:
            session.delete(c_item)

        session.commit()
        session.refresh(new_order)
        return {
            "status": "Venta realizada desde carrito",
            "factura": new_order.invoice_number,
            "total": total,
            "cliente": customer_name or "Consumidor Final",
            "warnings": stock_warnings,
        }

    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# --- 3. LISTAR ÓRDENES ---
@router.get("/", summary="Listar órdenes")
def list_orders(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Admin ve todas las órdenes, vendedor solo las propias."""
    if current_user.role == "ADMIN":
        orders = session.exec(select(Order)).all()
    else:
        orders = session.exec(select(Order).where(Order.user_id == current_user.id)).all()
    return orders


# --- 4. VER DETALLE DE FACTURA ---
@router.get("/{order_id}/invoice")
def get_invoice_detail(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Obtiene la factura completa. Admin ve cualquiera, vendedor solo la propia."""
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Factura no encontrada")

    if current_user.role != "ADMIN" and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tiene permiso para ver esta factura")

    return order