# tests/test_pricing.py
from decimal import Decimal
from datetime import datetime, timezone
import pytest
from app.services.pricing import calculate_transaction_fee


class TestCalculateTransactionFee:
    """Tests for the transaction fee calculation function."""
    
    def test_standard_fee_usd(self):
        """Standard tier, USD, weekday should use base rate."""
        fee = calculate_transaction_fee(
            amount=Decimal("100.00"),
            currency="USD",
            user_tier="standard",
            transaction_time=datetime(2026, 4, 15, 12, 0, tzinfo=timezone.utc),  # Wednesday
        )
        # 100 * 0.029 + 0.30 = 3.20
        assert fee == Decimal("3.20")
    
    def test_premium_fee_usd(self):
        """Premium tier should have lower rate."""
        fee = calculate_transaction_fee(
            amount=Decimal("100.00"),
            currency="USD",
            user_tier="premium",
            transaction_time=datetime(2026, 4, 15, 12, 0, tzinfo=timezone.utc),
        )
        # 100 * 0.015 + 0.10 = 1.60
        assert fee == Decimal("1.60")
    
    def test_enterprise_fee_usd(self):
        """Enterprise tier should have lowest rate."""
        fee = calculate_transaction_fee(
            amount=Decimal("100.00"),
            currency="USD",
            user_tier="enterprise",
            transaction_time=datetime(2026, 4, 15, 12, 0, tzinfo=timezone.utc),
        )
        # 100 * 0.005 + 0.05 = 0.55
        assert fee == Decimal("0.55")
    
    def test_international_surcharge(self):
        """Non-USD currencies should have 1% surcharge."""
        fee = calculate_transaction_fee(
            amount=Decimal("100.00"),
            currency="EUR",
            user_tier="standard",
            transaction_time=datetime(2026, 4, 15, 12, 0, tzinfo=timezone.utc),
        )
        # (100 * 0.029 + 0.30) + (100 * 0.01) = 4.20
        assert fee == Decimal("4.20")
    
    def test_weekend_surcharge(self):
        """Weekend transactions should have 0.5% surcharge."""
        fee = calculate_transaction_fee(
            amount=Decimal("100.00"),
            currency="USD",
            user_tier="standard",
            transaction_time=datetime(2026, 4, 18, 12, 0, tzinfo=timezone.utc),  # Saturday
        )
        # (100 * 0.029 + 0.30) + (100 * 0.005) = 3.70
        assert fee == Decimal("3.70")
    
    def test_volume_discount(self):
        """Amounts over $10,000 should get 20% discount."""
        fee = calculate_transaction_fee(
            amount=Decimal("15000.00"),
            currency="USD",
            user_tier="standard",
            transaction_time=datetime(2026, 4, 15, 12, 0, tzinfo=timezone.utc),
        )
        # (15000 * 0.029 + 0.30) * 0.8 = 348.24
        assert fee == Decimal("348.24")
    
    def test_negative_amount_raises_error(self):
        """Negative amounts should raise ValueError."""
        with pytest.raises(ValueError, match="Amount must be positive"):
            calculate_transaction_fee(
                amount=Decimal("-50.00"),
                currency="USD",
            )
    
    def test_zero_amount_raises_error(self):
        """Zero amounts should raise ValueError."""
        with pytest.raises(ValueError, match="Amount must be positive"):
            calculate_transaction_fee(
                amount=Decimal("0.00"),
                currency="USD",
            )
    
    def test_very_large_amount(self):
        """Very large amounts should not overflow or lose precision."""
        fee = calculate_transaction_fee(
            amount=Decimal("9999999.99"),
            currency="USD",
            user_tier="standard",
            transaction_time=datetime(2026, 4, 15, 12, 0, tzinfo=timezone.utc),
        )
        # (9999999.99 * 0.029 + 0.30) * 0.8 = 231999.99
        assert fee == Decimal("231999.99")
    
    def test_rounding_edge_case(self):
        """Fractions of cents should round correctly."""
        fee = calculate_transaction_fee(
            amount=Decimal("0.01"),
            currency="USD",
            user_tier="standard",
            transaction_time=datetime(2026, 4, 15, 12, 0, tzinfo=timezone.utc),
        )
        # (0.01 * 0.029 + 0.30) = 0.30029 -> 0.30
        assert fee == Decimal("0.30")
    
    def test_combined_surcharges(self):
        """International weekend transaction should apply both surcharges."""
        fee = calculate_transaction_fee(
            amount=Decimal("500.00"),
            currency="GBP",
            user_tier="standard",
            transaction_time=datetime(2026, 4, 18, 12, 0, tzinfo=timezone.utc),  # Saturday
        )
        # (500 * 0.029 + 0.30) + (500 * 0.01) + (500 * 0.005) = 22.30
        assert fee == Decimal("22.30")
