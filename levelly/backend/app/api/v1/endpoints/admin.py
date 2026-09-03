"""
LEVELLY — Admin Endpoints
Admin-only endpoints for managing product policies.
Admin cannot manipulate user consent directly.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_admin
from app.models.savings import CategorySavingPolicy
from app.models.investment import InvestmentProduct
from app.models.user import User
from app.models.financial_profile import FinancialProfile
from app.models.distress import DistressEvent
from app.models.credit import CreditRequest
from app.models.audit import AuditLog

router = APIRouter()


class CategoryPolicyUpdate(BaseModel):
    base_percentage: float
    min_percentage: Optional[float] = None
    max_percentage: Optional[float] = None
    description: Optional[str] = None


class InvestmentProductUpdate(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    risk_level: Optional[str] = None
    liquidity: Optional[str] = None
    holding_period: Optional[str] = None
    interest_or_coupon: Optional[str] = None
    fees: Optional[str] = None
    tax_notes: Optional[str] = None
    terms: Optional[str] = None
    description: Optional[str] = None
    min_investment: Optional[float] = None
    active: Optional[bool] = None


@router.get("/users")
def list_users(
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
    limit: int = 50,
):
    """List all users with their financial profiles."""
    users = db.query(User).limit(limit).all()
    result = []
    for u in users:
        profile = db.query(FinancialProfile).filter_by(user_id=u.id).first()
        result.append({
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role,
            "occupation": u.occupation,
            "is_active": u.is_active,
            "distress_level": profile.distress_level if profile else "N/A",
            "resilience_score": profile.resilience_score if profile else 0,
            "created_at": u.created_at.isoformat(),
        })
    return result


@router.get("/category-policies")
def get_category_policies(
    admin=Depends(get_current_admin), db: Session = Depends(get_db)
):
    """Get all category saving policies."""
    policies = db.query(CategorySavingPolicy).all()
    return [
        {
            "id": p.id,
            "category": p.category,
            "base_percentage": p.base_percentage,
            "min_percentage": p.min_percentage,
            "max_percentage": p.max_percentage,
            "is_active": p.is_active,
            "description": p.description,
        }
        for p in policies
    ]


@router.put("/category-policies/{category}")
def update_category_policy(
    category: str,
    request: CategoryPolicyUpdate,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update a category saving policy."""
    if request.base_percentage < 0 or request.base_percentage > 30:
        raise HTTPException(status_code=400, detail="Percentage must be 0-30")

    policy = (
        db.query(CategorySavingPolicy)
        .filter(CategorySavingPolicy.category == category.lower())
        .first()
    )
    if not policy:
        raise HTTPException(status_code=404, detail="Category policy not found")

    policy.base_percentage = request.base_percentage
    if request.min_percentage is not None:
        policy.min_percentage = request.min_percentage
    if request.max_percentage is not None:
        policy.max_percentage = request.max_percentage
    if request.description is not None:
        policy.description = request.description

    # Audit admin change
    audit = AuditLog(
        user_id=admin.id,
        actor_id=admin.id,
        event_type="admin_policy_change",
        action=f"updated_category_policy_{category}",
        entity_type="category_policy",
        extra_data={
            "category": category,
            "new_base_percentage": request.base_percentage,
        },
    )
    db.add(audit)
    db.commit()

    return {"message": f"Policy updated for {category}", "new_percentage": request.base_percentage}


@router.get("/investment-products")
def get_investment_products(
    admin=Depends(get_current_admin), db: Session = Depends(get_db)
):
    """List all investment products."""
    products = db.query(InvestmentProduct).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "type": p.product_type,
            "issuer": p.issuer,
            "risk_level": p.risk_level,
            "active": p.active,
            "min_investment": p.min_investment,
        }
        for p in products
    ]


@router.put("/investment-products/{product_id}")
def update_investment_product(
    product_id: int,
    request: InvestmentProductUpdate,
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Update investment product metadata."""
    product = db.query(InvestmentProduct).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in request.model_dump(exclude_none=True).items():
        setattr(product, field, value)

    audit = AuditLog(
        user_id=admin.id,
        actor_id=admin.id,
        event_type="admin_policy_change",
        action=f"updated_investment_product_{product_id}",
        entity_type="investment_product",
        extra_data=request.model_dump(exclude_none=True),
    )
    db.add(audit)
    db.commit()

    return {"message": "Product updated"}


@router.get("/distress-overview")
def get_distress_overview(
    admin=Depends(get_current_admin), db: Session = Depends(get_db)
):
    """Overview of all users' distress states."""
    profiles = db.query(FinancialProfile).all()
    return {
        "total_users": len(profiles),
        "by_level": {
            "LOW": sum(1 for p in profiles if p.distress_level == "LOW"),
            "MODERATE": sum(1 for p in profiles if p.distress_level == "MODERATE"),
            "HIGH": sum(1 for p in profiles if p.distress_level == "HIGH"),
            "SEVERE": sum(1 for p in profiles if p.distress_level == "SEVERE"),
        },
        "profiles": [
            {
                "user_id": p.user_id,
                "distress_level": p.distress_level,
                "distress_score": p.distress_score,
                "resilience_score": p.resilience_score,
            }
            for p in profiles
        ],
    }


@router.get("/audit-logs")
def get_audit_logs(
    admin=Depends(get_current_admin),
    db: Session = Depends(get_db),
    limit: int = 50,
):
    """List recent system audit logs for compliance tracking."""
    logs = (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": l.id,
            "user_id": l.user_id,
            "actor_id": l.actor_id,
            "event_type": l.event_type,
            "action": l.action,
            "entity_type": l.entity_type,
            "extra_data": l.extra_data,
            "created_at": l.created_at.isoformat() if l.created_at else None,
        }
        for l in logs
    ]
