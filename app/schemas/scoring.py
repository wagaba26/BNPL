from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class CreditScoreRequest(BaseModel):
    user_id: int
    mobile_money_statement: Optional[str] = None  # JSON string or file path
    bank_statement: Optional[str] = None  # JSON string or file path
    documents: Optional[dict] = None  # Additional documents/metadata


class CreditScoreResponse(BaseModel):
    user_id: int
    credit_score: int  # Typically 0-1000
    risk_level: str  # e.g., "low", "medium", "high"
    factors: Optional[dict] = None  # Factors affecting the score

