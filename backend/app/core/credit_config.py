"""
Credit Scoring Configuration Module

This module contains all configurable parameters for the credit scoring system.
Adjust these values to tune scoring behavior without modifying core logic.
"""
from decimal import Decimal
from typing import Dict
from app.models.credit_document import DocumentType


# ============================================================================
# INITIAL SCORING PARAMETERS
# ============================================================================

INITIAL_SCORE = 300
INITIAL_TIER = "TIER_1"
INITIAL_MAX_BNPL_LIMIT = Decimal("200000.00")


# ============================================================================
# DOCUMENT-BASED SCORING WEIGHTS (KYC - 40% of score)
# ============================================================================

DOCUMENT_WEIGHTS: Dict[DocumentType, int] = {
    DocumentType.MOBILE_MONEY_STATEMENT: 40,
    DocumentType.BANK_STATEMENT: 70,
    DocumentType.PROOF_OF_ADDRESS: 30,
    DocumentType.PAYSLIP: 60,
    DocumentType.EMPLOYMENT_CONTRACT: 50,
    DocumentType.BUSINESS_REGISTRATION: 50,
    DocumentType.LC1_LETTER: 20,
    DocumentType.OTHER: 10,
}

# Maximum points from "OTHER" documents (to prevent abuse)
MAX_OTHER_DOCUMENT_POINTS = 30


# ============================================================================
# REPAYMENT BEHAVIOR SCORING (40% of score)
# ============================================================================

# On-time payment rewards
ON_TIME_PAYMENT_POINTS = 5
MAX_ON_TIME_PAYMENT_POINTS = 100  # Cap for on-time payments

# Consecutive on-time streak bonus
CONSECUTIVE_ON_TIME_STREAK_BONUS = 10
STREAK_THRESHOLD = 3  # Number of consecutive on-time payments for bonus

# Early full repayment bonuses (based on loan amount)
EARLY_REPAYMENT_BONUS_SMALL = 15  # For loans < 500,000
EARLY_REPAYMENT_BONUS_MEDIUM = 25  # For loans 500,000 - 2,000,000
EARLY_REPAYMENT_BONUS_LARGE = 30  # For loans > 2,000,000
EARLY_REPAYMENT_THRESHOLD_SMALL = Decimal("500000.00")
EARLY_REPAYMENT_THRESHOLD_LARGE = Decimal("2000000.00")

# Late payment penalties
LATE_PAYMENT_PENALTY = -10  # Per late installment (>3 days overdue)
SEVERELY_LATE_PENALTY = -50  # >30 days overdue
DEFAULT_PENALTY = -100  # Loan defaulted

# Days considered "late" vs "severely late"
LATE_PAYMENT_DAYS = 3
SEVERELY_LATE_DAYS = 30


# ============================================================================
# USAGE & STABILITY SCORING (20% of score - simplified for v1)
# ============================================================================

SUCCESSFUL_BNPL_PURCHASE_BONUS = 5
MAX_USAGE_BONUS_POINTS = 50  # Cap for usage bonuses


# ============================================================================
# TIER DEFINITIONS
# ============================================================================

TIER_BANDS = {
    "TIER_0": (0, 199),      # score < 200
    "TIER_1": (200, 399),    # 200-399
    "TIER_2": (400, 599),    # 400-599
    "TIER_3": (600, 799),    # 600-799
    "TIER_4": (800, 1000),   # 800-1000
}


# ============================================================================
# MAX BNPL LIMITS PER TIER
# ============================================================================

MAX_BNPL_LIMITS: Dict[str, Decimal] = {
    "TIER_0": Decimal("0"),           # No BNPL allowed
    "TIER_1": Decimal("200000.00"),   # 200,000
    "TIER_2": Decimal("800000.00"),   # 800,000
    "TIER_3": Decimal("2000000.00"),  # 2,000,000
    "TIER_4": Decimal("5000000.00"),  # 5,000,000+
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def compute_tier_from_score(score: int) -> str:
    """Compute credit tier from score."""
    score = max(0, min(1000, score))  # Clamp to 0-1000
    
    for tier, (min_score, max_score) in TIER_BANDS.items():
        if min_score <= score <= max_score:
            return tier
    
    # Fallback (shouldn't happen)
    return "TIER_0"


def compute_limit_from_tier(tier: str) -> Decimal:
    """Compute max BNPL limit from tier."""
    return MAX_BNPL_LIMITS.get(tier, Decimal("0"))

