from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from typing import Optional


class CreditProfileResponse(BaseModel):
    id: int
    user_id: int
    score: int
    tier: str
    max_bnpl_limit: Decimal
    last_recalculated_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

