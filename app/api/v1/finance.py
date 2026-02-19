from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from app.database import get_session
from app.api.deps import get_current_user, get_admin_user
from app.models.user import User
from app.models.finance import Debt, Payment, PaymentCreate
from app.models.orders import Order

router = APIRouter(prefix="/finance", tags=["Finanzas y Reportes"])


@router.post("/debts/{debt_id}/pay")
def register_payment(
    debt_id: int,
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Registra un abono y actualiza el saldo de la deuda."""
    debt = session.get(Debt, debt_id)
    if not debt or debt.status == "PAID":
        raise HTTPException(status_code=400, detail="La deuda no existe o ya fue pagada")

    if payment_data.amount <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor a cero")

    if payment_data.amount > debt.balance:
        raise HTTPException(status_code=400, detail="El monto supera el saldo pendiente")

    new_payment = Payment(debt_id=debt.id, amount=payment_data.amount)
    debt.balance -= payment_data.amount

    if debt.balance <= 0:
        debt.status = "PAID"

    session.add(new_payment)
    session.add(debt)
    session.commit()
    return {"message": "Abono exitoso", "saldo_restante": debt.balance}


@router.get("/reports/dashboard")
def get_dashboard_stats(
    admin: User = Depends(get_admin_user),
    session: Session = Depends(get_session),
):
    """Métricas clave para el negocio (solo ADMIN)."""
    total_revenue = session.exec(select(func.sum(Order.total))).one() or 0
    total_orders = session.exec(select(func.count(Order.id))).one() or 0
    total_debt_balance = session.exec(select(func.sum(Debt.balance))).one() or 0

    return {
        "ventas_totales": total_revenue,
        "numero_pedidos": total_orders,
        "cartera_pendiente": total_debt_balance,
    }


@router.get("/debts/pending")
def list_pending_debts(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Lista todas las deudas pendientes."""
    statement = select(Debt).where(Debt.status == "OPEN")
    return session.exec(statement).all()