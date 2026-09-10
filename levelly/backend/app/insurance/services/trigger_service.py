"""
LEVELLY IncomeShield — Trigger Evaluation Service
Enforces the core rule: An external event detected NEVER equates directly to a payout.
Evaluates deterministic parametric policy conditions against observed sensor/telemetry data.
"""
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.insurance.models import (
    InsurancePolicy,
    InsuranceEvent,
    InsuranceTriggerEvaluation,
    InsurancePayout,
)
from app.insurance.integrations.provider import get_insurance_provider
from app.models.audit import AuditLog
from app.services.notification_service import NotificationService


class InsuranceTriggerService:
    """Evaluates policies against external disruption events."""

    def __init__(self, db: Session):
        self.db = db
        self.provider = get_insurance_provider()
        self.notifications = NotificationService(db)

    def evaluate_policy_for_event(
        self,
        policy_id: int,
        event_id: int,
    ) -> InsuranceTriggerEvaluation:
        """
        Evaluate policy conditions against an active event.
        Returns InsuranceTriggerEvaluation and coordinates payout initiation if REACHED.
        """
        policy = self.db.query(InsurancePolicy).filter_by(id=policy_id).first()
        if not policy:
            raise ValueError(f"Policy {policy_id} not found")

        event = self.db.query(InsuranceEvent).filter_by(id=event_id).first()
        if not event:
            raise ValueError(f"Event {event_id} not found")

        # Check existing evaluation
        existing_eval = (
            self.db.query(InsuranceTriggerEvaluation)
            .filter_by(policy_id=policy.id, event_id=event.id)
            .first()
        )

        policy_dict = {
            "policy_id": policy.id,
            "policy_number": policy.policy_number,
            "coverage_limit": policy.coverage_limit,
            "covered_work_zone": policy.covered_work_zone,
        }
        event_dict = {
            "event_id": event.id,
            "event_type": event.event_type,
            "zone": event.zone,
            "telemetry_data": event.telemetry_data or {},
        }

        eval_result = self.provider.evaluate_trigger(policy_dict, event_dict)
        status = eval_result.get("status", "NOT_REACHED")
        reason = eval_result.get("reason", "Condition evaluated")
        threshold = eval_result.get("threshold", "Threshold")
        observed = eval_result.get("observed_value", "Observed")
        required = eval_result.get("required_value", "Required")

        if existing_eval:
            existing_eval.status = status
            existing_eval.reason = reason
            existing_eval.threshold = threshold
            existing_eval.observed_value = observed
            existing_eval.required_value = required
            existing_eval.evaluated_at = datetime.now(timezone.utc)
            evaluation = existing_eval
        else:
            evaluation = InsuranceTriggerEvaluation(
                policy_id=policy.id,
                event_id=event.id,
                trigger_type=event.event_type,
                threshold=threshold,
                observed_value=observed,
                required_value=required,
                status=status,
                reason=reason,
                evaluated_at=datetime.now(timezone.utc),
            )
            self.db.add(evaluation)

        # Audit log for evaluation
        audit = AuditLog(
            user_id=policy.user_id,
            event_type="insurance_trigger_evaluated",
            action=f"Evaluated policy {policy.policy_number} against {event.event_type}: {status}",
            entity_type="insurance_trigger_evaluation",
            entity_id=evaluation.id if evaluation.id else None,
        )
        self.db.add(audit)

        # Handle Payout lifecycle based on outcome
        if status == "REACHED":
            # Check if payout already created
            existing_payout = (
                self.db.query(InsurancePayout)
                .filter_by(policy_id=policy.id, event_id=event.id)
                .first()
            )
            suggested_amount = eval_result.get("suggested_payout_amount", 750.0)

            if not existing_payout:
                payout = InsurancePayout(
                    policy_id=policy.id,
                    event_id=event.id,
                    payout_id_from_partner=f"PAYOUT-{uuid.uuid4().hex[:8].upper()}",
                    amount=suggested_amount,
                    currency="INR",
                    status="PROCESSING",
                    reason=f"Parametric trigger confirmed for {event.event_type.replace('_', ' ').title()}",
                    destination_reference="Linked Bank Account (Direct UPI)",
                    destination_type="LINKED_ACCOUNT",
                    processed_at=datetime.now(timezone.utc),
                )
                self.db.add(payout)
                self.db.flush()

                # Audit log for payout initiation
                payout_audit = AuditLog(
                    user_id=policy.user_id,
                    event_type="insurance_payout_initiated",
                    action=f"Initiated payout of ₹{suggested_amount} for policy {policy.policy_number}",
                    entity_type="insurance_payout",
                    entity_id=payout.id,
                )
                self.db.add(payout_audit)

                # Send Notification
                self.notifications.create(
                    user_id=policy.user_id,
                    title="Coverage Trigger Reached",
                    message=f"Disruption conditions met policy criteria. Your payout of ₹{suggested_amount:.0f} is processing.",
                    notification_type="insurance_trigger_reached",
                    priority="high",
                    action_url=f"/incomeshield/payouts/{payout.id}",
                )
        else:
            # NOT_REACHED: No payout created. Notify user gracefully.
            self.notifications.create(
                user_id=policy.user_id,
                title="Event Monitored",
                message=f"Conditions for {event.event_type.replace('_', ' ').title()} did not meet your policy trigger. Your coverage remains active.",
                notification_type="insurance_trigger_not_reached",
                priority="normal",
                action_url=f"/incomeshield/events/{event.id}",
            )

        self.db.commit()
        self.db.refresh(evaluation)
        return evaluation
