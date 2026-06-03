# app/services/pricing.py
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime, timezone
from typing import Optional


def calculate_transaction_fee(
    amount: Decimal,
    currency: str,
    user_tier: str = "standard",
    transaction_time: Optional[datetime] = None,
) -> Decimal:
    """
    Calculate transaction fee based on amount, currency, user tier, and time.
    
    Fees:
    - Standard: 2.9% + $0.30
    - Premium: 1.5% + $0.10
    - Enterprise: 0.5% + $0.05
    
    Additional fees:
    - International currency: +1% 
    - Weekend/holiday: +0.5%
    - Amount over $10,000: volume discount of 20% off fee
    """
    if amount <= 0:
        raise ValueError("Amount must be positive")
    
    fee_percentages = {
        "standard": Decimal("0.029"),
        "premium": Decimal("0.015"),
        "enterprise": Decimal("0.005"),
    }
    
    base_fee_percentage = fee_percentages.get(user_tier, Decimal("0.029"))
    base_fee = (amount * base_fee_percentage) + Decimal("0.30")
    
    # International surcharge
    if currency != "USD":
        base_fee += amount * Decimal("0.01")
    
    # Weekend surcharge
    if transaction_time:
        if transaction_time.weekday() >= 5:  # Saturday or Sunday
            base_fee += amount * Decimal("0.005")
    
    # Volume discount
    if amount > Decimal("10000"):
        base_fee = base_fee * Decimal("0.8")
    
    # Round to nearest cent
    return base_fee.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
