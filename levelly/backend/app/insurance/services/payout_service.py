"""
LEVELLY IncomeShield — Payout Service
Manages insurance payout completion and explicit user-driven Safety Wallet allocation.
DOES NOT automatically transfer payouts; respects worker autonomy.
"""
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.insurance.models import InsurancePayout, InsurancePolicy
from app.models.wallet import Wallet
from app.models.savings import SavingsTransaction
from app.models.audit import AuditLog
from app.services.notification_service import NotificationService


class InsurancePayoutService:
    """Manages claim payouts and coordinates with the existing LEVELLY Safety Wallet."""

    def __init__(self, db: Session):
        self.db = db
        self.notifications = NotificationService(db)

    def complete_payout(self, payout_id: int) -> InsurancePayout:
        """Mark payout as settled by the insurance partner."""
        payout = self.db.query(InsurancePayout).filter_by(id=payout_id).first()
        if not payout:
            raise HTTPException(status_code=404, detail="Payout record not found")

        policy = self.db.query(InsurancePolicy).filter_by(id=payout.policy_id).first()
        payout.status = "COMPLETED"
        payout.processed_at = datetime.now(timezone.utc)

        if policy:
            audit = AuditLog(
                user_id=policy.user_id,
                event_type="insurance_payout_completed",
                action=f"Settled payout {payout.payout_id_from_partner} of ₹{payout.amount or 0:.0f}",
                entity_type="insurance_payout",
                entity_id=payout.id,
            )
            self.db.add(audit)

            self.notifications.create(
                user_id=policy.user_id,
                title="Payout Completed",
                message=f"₹{payout.amount or 0:.0f} has been deposited to your {payout.destination_reference}.",
                notification_type="insurance_payout_completed",
                priority="normal",
                action_url=f"/incomeshield/payouts/{payout.id}",
            )

        self.db.commit()
        self.db.refresh(payout)
        return payout

    def move_to_safety_wallet(
        self,
        user_id: int,
        payout_id: int,
        amount: float,
    ) -> Dict[str, Any]:
        """
        User-initiated allocation of claim payout into their existing LEVELLY Safety Wallet.
        NEVER automatic; strictly invoked by explicit user choice.
        """
        payout = self.db.query(InsurancePayout).filter_by(id=payout_id).first()
        if not payout:
            raise HTTPException(status_code=404, detail="Payout not found")

        policy = self.db.query(InsurancePolicy).filter_by(id=payout.policy_id).first()
        if not policy or policy.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to manage this payout")

        if amount <= 0:
            raise HTTPException(status_code=400, detail="Transfer amount must be greater than zero")

        if payout.amount and amount > payout.amount:
            raise HTTPException(status_code=400, detail=f"Cannot transfer more than payout amount (₹{payout.amount})")

        # Reuse existing Safety Wallet
        wallet = (
            self.db.query(Wallet)
            .filter(Wallet.user_id == user_id, Wallet.wallet_type == "SAFETY", Wallet.is_active == True)
            .first()
        )
        if not wallet:
            wallet = Wallet(
                user_id=user_id,
                wallet_type="SAFETY",
                balance=0.0,
                target_amount=10000.0,
                currency="INR",
                is_active=True,
            )
            self.db.add(wallet)
            self.db.flush()

        initial_balance = wallet.balance
        wallet.balance = round(wallet.balance + amount, 2)

        # Record savings transaction
        savings_txn = SavingsTransaction(
            user_id=user_id,
            amount=amount,
            transaction_type="insurance_payout_allocation",
            category_context="incomeshield_payout",
            balance_before=initial_balance,
            balance_after=wallet.balance,
        )
        self.db.add(savings_txn)

        # Update payout destination record
        payout.destination_type = "SAFETY_WALLET"

        # Record audit log
        audit = AuditLog(
            user_id=user_id,
            event_type="safety_wallet_deposit",
            action=f"Transferred ₹{amount:.0f} from IncomeShield payout #{payout.id} into Safety Wallet",
            entity_type="wallet",
            entity_id=wallet.id,
        )
        self.db.add(audit)

        self.db.commit()
        self.db.refresh(wallet)

        return {
            "success": True,
            "message": f"Transferred ₹{amount:.0f} to your Safety Wallet.",
            "transferred_amount": amount,
            "safety_wallet_balance": wallet.balance,
            "safety_wallet_target": wallet.target_amount,
            "progress_percentage": wallet.progress_percentage,
            "shortfall": max(0.0, (wallet.target_amount or 10000.0) - wallet.balance),
        }
