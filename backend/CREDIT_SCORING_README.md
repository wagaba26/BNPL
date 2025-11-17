# Credit Scoring Subsystem

This document describes the credit scoring subsystem for the BNPL platform.

## Overview

The credit scoring system maintains a score from 0-1000 for each customer and groups them into credit tiers (TIER_0 to TIER_4). The system uses both KYC/document-based signals and behavioral signals (repayments, late payments, usage).

## Architecture

### Models

1. **CreditProfile** - One-to-one with User (for CUSTOMER role)
   - `score` (0-1000)
   - `tier` (TIER_0 to TIER_4)
   - `max_bnpl_limit` (based on tier)
   - `last_recalculated_at` (timestamp of last full recalculation)

2. **CreditScoreEvent** - History of all score changes
   - `event_type` (e.g., "DOCUMENT_APPROVED", "ON_TIME_PAYMENT", "LATE_PAYMENT")
   - `delta` (score change, positive or negative)
   - `score_before` and `score_after`
   - `metadata` (JSON with additional details)

3. **CreditDocument** - KYC document uploads
   - `document_type` (enum: MOBILE_MONEY_STATEMENT, BANK_STATEMENT, etc.)
   - `file_path` (path to stored file)
   - `status` (PENDING, APPROVED, REJECTED)
   - `reviewed_at` and `reviewer_id` (for admin review)

### Scoring Logic

The scoring system is rule-based (v1) and composed of:

- **40% Documents/KYC** - Points for approved documents
- **40% Repayment Behavior** - Points for on-time payments, penalties for late payments
- **20% Usage/Stability** - Points for successful BNPL purchases

#### Document Weights

- Mobile money statement: +40 points
- Bank statement: +70 points
- Proof of address: +30 points
- Payslip: +60 points
- Employment contract: +50 points
- Business registration: +50 points
- LC1 letter: +20 points
- Other: +10 points (capped at 30 total)

#### Payment Behavior

- On-time payment: +5 points per installment (capped at 100)
- Consecutive on-time streak (3+): +10 bonus
- Early full repayment: +15 to +30 (based on loan size)
- Late payment (>3 days): -10 points
- Severely late (>30 days): -50 points
- Default: -100 points

#### Tiers and Limits

- **TIER_0** (0-199): No BNPL allowed
- **TIER_1** (200-399): 200,000 limit
- **TIER_2** (400-599): 800,000 limit
- **TIER_3** (600-799): 2,000,000 limit
- **TIER_4** (800-1000): 5,000,000+ limit

## API Endpoints

### Customer Endpoints

- `GET /credit/profile/me` - Get current credit profile
- `GET /credit/events/me` - Get paginated credit score events
- `POST /credit/documents` - Upload a document (multipart form)
- `GET /credit/documents/me` - List all uploaded documents
- `GET /credit/documents/status` - Get document status checklist
- `POST /credit/recalculate/me` - Recalculate score from scratch

### Admin Endpoints

- `POST /credit/documents/{document_id}/review` - Review a document (APPROVE/REJECT)
- `GET /credit/documents/{document_id}/download` - Download a document

## Service Layer

The core scoring logic is in `app/services/credit_scoring.py`:

- `get_or_create_credit_profile(user_id)` - Get or create profile
- `apply_score_change(user_id, delta, event_type, metadata)` - Apply score change
- `handle_document_approved(document)` - Handle document approval
- `handle_installment_payment(installment)` - Handle payment
- `handle_loan_status_change(loan, previous_status, new_status)` - Handle loan status
- `recalculate_full_score(user_id)` - Full recalculation

## Configuration

All scoring rules are in `app/core/credit_config.py` for easy tuning without modifying core logic.

## Integration Points

To integrate credit scoring with payment processing:

1. **When an installment is paid:**
   ```python
   from app.services.credit_scoring import handle_installment_payment
   
   installment.paid = True
   installment.paid_at = datetime.now(timezone.utc)
   handle_installment_payment(db, installment)
   ```

2. **When loan status changes:**
   ```python
   from app.services.credit_scoring import handle_loan_status_change
   
   previous_status = loan.status
   loan.status = LoanStatus.PAID
   handle_loan_status_change(db, loan, previous_status, loan.status)
   ```

3. **When a document is approved:**
   ```python
   from app.services.credit_scoring import handle_document_approved
   
   document.status = DocumentStatus.APPROVED
   handle_document_approved(db, document)
   ```

## Database Migration

Run the Alembic migration to create the new tables:

```bash
cd backend
alembic upgrade head
```

## Testing

Run the test suite:

```bash
cd backend
pytest tests/test_credit_scoring.py -v
```

## Future Enhancements

The system is designed to be modular so that ML models can be plugged in later:

1. Replace rule-based scoring with ML model predictions
2. Add more behavioral signals (login frequency, app usage, etc.)
3. Implement real-time scoring updates
4. Add score explanations/breakdowns for customers

