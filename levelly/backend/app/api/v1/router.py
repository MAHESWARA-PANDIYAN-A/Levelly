"""
LEVELLY — API v1 Router
"""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    users,
    wallets,
    transactions,
    payments,
    expenses,
    income,
    financial_health,
    credit,
    investments,
    notifications,
    coach,
    admin,
    nudges,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(wallets.router, prefix="/wallets", tags=["Wallets"])
api_router.include_router(transactions.router, prefix="/transactions", tags=["Transactions"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["Expenses"])
api_router.include_router(income.router, prefix="/income", tags=["Income"])
api_router.include_router(financial_health.router, prefix="/financial-health", tags=["Financial Health"])
api_router.include_router(credit.router, prefix="/credit", tags=["Credit"])
api_router.include_router(investments.router, prefix="/investments", tags=["Investments"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
api_router.include_router(coach.router, prefix="/coach", tags=["Levelly Coach"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(nudges.router, prefix="/nudges", tags=["Nudges"])
