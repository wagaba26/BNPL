import pytest
from decimal import Decimal
from app.services.payment_schedule import payment_schedule_service
from app.services.scoring import credit_scoring_service
from app.schemas.scoring import CreditScoreRequest


def test_calculate_loan_amounts():
    """Test loan amount calculation."""
    deposit, loan, total = payment_schedule_service.calculate_loan_amounts(
        product_price=Decimal("1000.00"),
        deposit_percentage=Decimal("10.00"),
        interest_rate=Decimal("12.00"),
    )

    assert deposit == Decimal("100.00")
    assert loan == Decimal("900.00")
    # Total = 900 + (900 * 0.12) = 900 + 108 = 1008
    assert total == Decimal("1008.00")


def test_calculate_credit_score(db, test_user):
    """Test credit score calculation."""
    request = CreditScoreRequest(
        user_id=test_user.id,
        mobile_money_statement="test data",
        bank_statement="test data",
    )

    result = credit_scoring_service.calculate_credit_score(db, request)

    assert result.user_id == test_user.id
    assert 0 <= result.credit_score <= 1000
    assert result.risk_level in ["low", "medium", "high"]
    assert result.factors is not None

