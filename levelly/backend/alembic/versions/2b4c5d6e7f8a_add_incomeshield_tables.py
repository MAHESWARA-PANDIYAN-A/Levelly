"""add_incomeshield_tables

Revision ID: 2b4c5d6e7f8a
Revises: 1ac0710e0c5c
Create Date: 2026-09-04 11:25:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = '2b4c5d6e7f8a'
down_revision: Union[str, None] = '1ac0710e0c5c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. insurance_partners
    op.create_table(
        'insurance_partners',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('partner_type', sa.String(length=64), server_default='LICENSED_INSURER', nullable=False),
        sa.Column('active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('contact_info', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_insurance_partners_id'), 'insurance_partners', ['id'], unique=False)
    op.create_index(op.f('ix_insurance_partners_code'), 'insurance_partners', ['code'], unique=True)

    # 2. insurance_plans
    op.create_table(
        'insurance_plans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('partner_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('code', sa.String(length=64), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('premium', sa.Float(), nullable=False),
        sa.Column('premium_frequency', sa.String(length=32), server_default='weekly', nullable=False),
        sa.Column('coverage_limit', sa.Float(), nullable=False),
        sa.Column('policy_duration', sa.String(length=64), server_default='7 days', nullable=False),
        sa.Column('covered_events', sa.JSON(), nullable=True),
        sa.Column('trigger_conditions', sa.JSON(), nullable=True),
        sa.Column('waiting_period', sa.String(length=64), server_default='24 hours', nullable=False),
        sa.Column('exclusions', sa.JSON(), nullable=True),
        sa.Column('coverage_area_rules', sa.JSON(), nullable=True),
        sa.Column('active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['partner_id'], ['insurance_partners.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_insurance_plans_id'), 'insurance_plans', ['id'], unique=False)
    op.create_index(op.f('ix_insurance_plans_code'), 'insurance_plans', ['code'], unique=True)

    # 3. insurance_policies
    op.create_table(
        'insurance_policies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('partner_id', sa.Integer(), nullable=True),
        sa.Column('policy_number', sa.String(length=128), nullable=False),
        sa.Column('status', sa.String(length=32), server_default='ACTIVE', nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('premium', sa.Float(), nullable=False),
        sa.Column('coverage_limit', sa.Float(), nullable=False),
        sa.Column('covered_work_zone', sa.String(length=128), server_default='Chennai Delivery Zone', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['partner_id'], ['insurance_partners.id'], ),
        sa.ForeignKeyConstraint(['plan_id'], ['insurance_plans.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_insurance_policies_id'), 'insurance_policies', ['id'], unique=False)
    op.create_index(op.f('ix_insurance_policies_user_id'), 'insurance_policies', ['user_id'], unique=False)
    op.create_index(op.f('ix_insurance_policies_plan_id'), 'insurance_policies', ['plan_id'], unique=False)
    op.create_index(op.f('ix_insurance_policies_policy_number'), 'insurance_policies', ['policy_number'], unique=True)
    op.create_index(op.f('ix_insurance_policies_status'), 'insurance_policies', ['status'], unique=False)

    # 4. insurance_consents
    op.create_table(
        'insurance_consents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('plan_id', sa.Integer(), nullable=False),
        sa.Column('terms_version', sa.String(length=32), server_default='v1.0', nullable=False),
        sa.Column('confirmed', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('confirmed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['plan_id'], ['insurance_plans.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_insurance_consents_id'), 'insurance_consents', ['id'], unique=False)
    op.create_index(op.f('ix_insurance_consents_user_id'), 'insurance_consents', ['user_id'], unique=False)

    # 5. insurance_events
    op.create_table(
        'insurance_events',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('event_type', sa.String(length=64), nullable=False),
        sa.Column('zone', sa.String(length=128), nullable=False),
        sa.Column('start_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration', sa.String(length=64), server_default='Ongoing', nullable=False),
        sa.Column('source', sa.String(length=128), server_default='IMD / Weather Telemetry', nullable=False),
        sa.Column('source_reference', sa.String(length=128), nullable=True),
        sa.Column('verification_status', sa.String(length=32), server_default='VERIFIED', nullable=False),
        sa.Column('severity', sa.String(length=32), server_default='MODERATE', nullable=False),
        sa.Column('telemetry_data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_insurance_events_id'), 'insurance_events', ['id'], unique=False)
    op.create_index(op.f('ix_insurance_events_event_type'), 'insurance_events', ['event_type'], unique=False)
    op.create_index(op.f('ix_insurance_events_zone'), 'insurance_events', ['zone'], unique=False)
    op.create_index(op.f('ix_insurance_events_verification_status'), 'insurance_events', ['verification_status'], unique=False)

    # 6. insurance_trigger_evaluations
    op.create_table(
        'insurance_trigger_evaluations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('policy_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=False),
        sa.Column('trigger_type', sa.String(length=64), nullable=False),
        sa.Column('threshold', sa.String(length=128), nullable=False),
        sa.Column('observed_value', sa.String(length=128), nullable=False),
        sa.Column('required_value', sa.String(length=128), nullable=False),
        sa.Column('status', sa.String(length=32), server_default='PENDING', nullable=False),
        sa.Column('evaluated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('reason', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['insurance_events.id'], ),
        sa.ForeignKeyConstraint(['policy_id'], ['insurance_policies.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_insurance_trigger_evaluations_id'), 'insurance_trigger_evaluations', ['id'], unique=False)
    op.create_index(op.f('ix_insurance_trigger_evaluations_policy_id'), 'insurance_trigger_evaluations', ['policy_id'], unique=False)
    op.create_index(op.f('ix_insurance_trigger_evaluations_event_id'), 'insurance_trigger_evaluations', ['event_id'], unique=False)
    op.create_index(op.f('ix_insurance_trigger_evaluations_status'), 'insurance_trigger_evaluations', ['status'], unique=False)

    # 7. insurance_payouts
    op.create_table(
        'insurance_payouts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('policy_id', sa.Integer(), nullable=False),
        sa.Column('event_id', sa.Integer(), nullable=True),
        sa.Column('payout_id_from_partner', sa.String(length=128), nullable=True),
        sa.Column('amount', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=16), server_default='INR', nullable=False),
        sa.Column('status', sa.String(length=32), server_default='PENDING', nullable=False),
        sa.Column('reason', sa.String(length=255), nullable=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('destination_reference', sa.String(length=128), server_default='Linked Bank Account (Direct UPI)', nullable=True),
        sa.Column('destination_type', sa.String(length=64), server_default='LINKED_ACCOUNT', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['event_id'], ['insurance_events.id'], ),
        sa.ForeignKeyConstraint(['policy_id'], ['insurance_policies.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_insurance_payouts_id'), 'insurance_payouts', ['id'], unique=False)
    op.create_index(op.f('ix_insurance_payouts_policy_id'), 'insurance_payouts', ['policy_id'], unique=False)
    op.create_index(op.f('ix_insurance_payouts_payout_id_from_partner'), 'insurance_payouts', ['payout_id_from_partner'], unique=True)
    op.create_index(op.f('ix_insurance_payouts_status'), 'insurance_payouts', ['status'], unique=False)

    # 8. insurance_documents
    op.create_table(
        'insurance_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('policy_id', sa.Integer(), nullable=True),
        sa.Column('plan_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('document_type', sa.String(length=64), server_default='POLICY_SCHEDULE', nullable=False),
        sa.Column('file_url', sa.String(length=512), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['plan_id'], ['insurance_plans.id'], ),
        sa.ForeignKeyConstraint(['policy_id'], ['insurance_policies.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_insurance_documents_id'), 'insurance_documents', ['id'], unique=False)
    op.create_index(op.f('ix_insurance_documents_policy_id'), 'insurance_documents', ['policy_id'], unique=False)
    op.create_index(op.f('ix_insurance_documents_plan_id'), 'insurance_documents', ['plan_id'], unique=False)


def downgrade() -> None:
    op.drop_table('insurance_documents')
    op.drop_table('insurance_payouts')
    op.drop_table('insurance_trigger_evaluations')
    op.drop_table('insurance_events')
    op.drop_table('insurance_consents')
    op.drop_table('insurance_policies')
    op.drop_table('insurance_plans')
    op.drop_table('insurance_partners')
