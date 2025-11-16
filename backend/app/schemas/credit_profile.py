from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime


class CreditProfileResponse(BaseModel):
    id: int
    user_id: int
    score: int
    tier: str
    max_bnpl_limit: Decimal
    last_updated_at: datetime

    class Config:
        from_attributes = True

