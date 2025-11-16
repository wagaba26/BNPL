from app.schemas.user import User, UserCreate, UserUpdate, UserResponse
from app.schemas.auth import Token, TokenData, LoginRequest
from app.schemas.retailer import Retailer, RetailerCreate, RetailerUpdate, RetailerResponse
from app.schemas.mfi import MFI, MFICreate, MFIUpdate, MFIResponse
from app.schemas.product import Product, ProductCreate, ProductUpdate, ProductResponse
from app.schemas.loan import (
    Loan,
    LoanCreate,
    LoanUpdate,
    LoanResponse,
    LoanApproval,
    PaymentSchedule,
    PaymentScheduleResponse,
)
from app.schemas.scoring import CreditScoreRequest, CreditScoreResponse
from app.schemas.user_asset import UserAsset, UserAssetCreate, UserAssetResponse
from app.schemas.trade_in import TradeInRequest, TradeInRequestCreate, TradeInRequestResponse

__all__ = [
    "User",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "Token",
    "TokenData",
    "LoginRequest",
    "Retailer",
    "RetailerCreate",
    "RetailerUpdate",
    "RetailerResponse",
    "MFI",
    "MFICreate",
    "MFIUpdate",
    "MFIResponse",
    "Product",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "Loan",
    "LoanCreate",
    "LoanUpdate",
    "LoanResponse",
    "LoanApproval",
    "PaymentSchedule",
    "PaymentScheduleResponse",
    "CreditScoreRequest",
    "CreditScoreResponse",
    "UserAsset",
    "UserAssetCreate",
    "UserAssetResponse",
    "TradeInRequest",
    "TradeInRequestCreate",
    "TradeInRequestResponse",
]

