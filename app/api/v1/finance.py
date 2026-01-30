from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from app.database import get_session
from app.models.finance import Debt, Payment, PaymentCreate
from app.models.orders import Order

router = APIRouter(prefix="/finance", tags=["Finanzas y Reportes"])

@router.post("/debts/{debt_id}/pay")
def register_payment(
    debt_id: int, 
    payment_data: PaymentCreate, 
    session: Session = Depends(get_session)
):
    """Registra un abono y actualiza el saldo de la deuda"""
    debt = session.get(Debt, debt_id)
    if not debt or debt.status == "PAID":
        raise HTTPException(status_code=400, detail="La deuda no existe o ya fue pagada")

    if payment_data.amount > debt.balance:
        raise HTTPException(status_code=400, detail="El monto supera el saldo pendiente")

    # Registrar el pago
    new_payment = Payment(debt_id=debt.id, amount=payment_data.amount)
    debt.balance -= payment_data.amount
    
    if debt.balance <= 0:
        debt.status = "PAID"

    session.add(new_payment)
    session.add(debt)
    session.commit()
    return {"message": "Abono exitoso", "saldo_restante": debt.balance}

@router.get("/reports/dashboard")
def get_dashboard_stats(session: Session = Depends(get_session)):
    """Métricas clave para el negocio"""
    # Ventas totales históricas
    total_revenue = session.exec(select(func.sum(Order.total))).one() or 0
    # Cantidad de pedidos realizados
    total_orders = session.exec(select(func.count(Order.id))).one() or 0
    # Dinero total que nos deben (cartera)
    total_debt_balance = session.exec(select(func.sum(Debt.balance))).one() or 0

    return {
        "ventas_totales": total_revenue,
        "numero_pedidos": total_orders,
        "cartera_pendiente": total_debt_balance
    }

# ... (imports anteriores)

@router.get("/debts/pending")
def list_pending_debts(session: Session = Depends(get_session)):
    """Lista todas las personas que deben dinero y cuánto deben"""
    statement = select(Debt).where(Debt.status == "OPEN")
    results = session.exec(statement).all()
    return results