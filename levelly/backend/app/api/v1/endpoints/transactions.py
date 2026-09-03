"""
LEVELLY — Transactions Endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.transaction import ExpenseTransaction, IncomeTransaction
from app.models.savings import SavingsTransaction

router = APIRouter()


@router.get("/")
def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 30,
    offset: int = 0,
    transaction_type: Optional[str] = None,
):
    """Get all transactions (income + expenses + savings) in combined timeline."""
    result = []

    # Income transactions
    income_txns = (
        db.query(IncomeTransaction)
        .filter(IncomeTransaction.user_id == current_user.id)
        .order_by(IncomeTransaction.transaction_date.desc())
        .all()
    )

    for t in income_txns:
        result.append({
            "id": f"income_{t.id}",
            "type": "income",
            "amount": t.amount,
            "direction": "credit",
            "category": "income",
            "description": t.description or f"Payout from {t.source}",
            "date": t.transaction_date.isoformat(),
            "status": t.status,
        })

    # Expense transactions
    expense_txns = (
        db.query(ExpenseTransaction)
        .filter(ExpenseTransaction.user_id == current_user.id)
        .order_by(ExpenseTransaction.transaction_date.desc())
        .all()
    )

    for t in expense_txns:
        result.append({
            "id": f"expense_{t.id}",
            "type": "expense",
            "amount": t.amount,
            "direction": "debit",
            "category": t.category,
            "description": t.description or f"{t.category.title()} payment",
            "save_at_pay": t.savings_added > 0 if t.savings_added else False,
            "savings_added": t.savings_added or 0,
            "date": t.transaction_date.isoformat(),
            "status": t.status,
        })

    # Savings transactions
    savings_txns = (
        db.query(SavingsTransaction)
        .filter(SavingsTransaction.user_id == current_user.id)
        .order_by(SavingsTransaction.created_at.desc())
        .all()
    )

    for t in savings_txns:
        direction = "credit" if t.amount > 0 else "debit"
        result.append({
            "id": f"savings_{t.id}",
            "type": "savings",
            "amount": abs(t.amount),
            "direction": direction,
            "category": "savings",
            "description": (
                f"Save-at-Pay ({t.category_context})"
                if t.transaction_type == "save_at_pay"
                else f"Safety Wallet {t.transaction_type}"
            ),
            "date": t.created_at.isoformat(),
            "status": "completed",
        })

    # Sort all by date, apply pagination
    result.sort(key=lambda x: x["date"], reverse=True)

    if transaction_type:
        result = [t for t in result if t["type"] == transaction_type]

    total = len(result)
    paginated = result[offset : offset + limit]

    return {
        "transactions": paginated,
        "total": total,
        "limit": limit,
        "offset": offset,
    }
