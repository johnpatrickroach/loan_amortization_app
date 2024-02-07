import pytest
from api.utils import calculate_amortization_amount
from api.enums import PaymentFrequency


# Happy path tests with various realistic test values
@pytest.mark.parametrize("principal, interest_rate, period, payment_frequency, expected", [
    (150000, 0.1, 36, PaymentFrequency.MONTHLY, 4840.08),  # ID: HP-1
    (200000, 0.05, 24, PaymentFrequency.MONTHLY, 8774.28),  # ID: HP-2
    (100000, 0.07, 12, PaymentFrequency.SEMIMONTHLY, 8492.16),  # ID: HP-3
    (50000, 0.08, 48, PaymentFrequency.QUARTERLY, 1630.09),  # ID: HP-4
], ids=["HP-1", "HP-2", "HP-3", "HP-4"])
def test_calculate_amortization_amount_happy_path(principal, interest_rate, period, payment_frequency, expected):
    # Act
    result = calculate_amortization_amount(principal, interest_rate, period, payment_frequency)

    # Assert
    assert result == expected


# Edge cases
@pytest.mark.parametrize("principal, interest_rate, period, payment_frequency, expected", [
    (0, 0.1, 36, PaymentFrequency.MONTHLY, 0.0),  # ID: EC-1: Zero principal
    (150000, 0.1, 1, PaymentFrequency.MONTHLY, 151250.0),  # ID: EC-2: Single period
], ids=["EC-1", "EC-2"])
def test_calculate_amortization_amount_edge_cases(principal, interest_rate, period, payment_frequency, expected):
    # Act
    result = calculate_amortization_amount(principal, interest_rate, period, payment_frequency)

    # Assert
    assert result == expected


# Error cases
@pytest.mark.parametrize("principal, interest_rate, period, payment_frequency, exception", [
    (150000, 0, 36, PaymentFrequency.MONTHLY, ZeroDivisionError),  # ID: ERR-1: Zero interest rate
    ("string", 0.1, 36, PaymentFrequency.MONTHLY, TypeError),  # ID: ERR-2: String principal
    (150000, "string", 36, PaymentFrequency.MONTHLY, TypeError),  # ID: ERR-3: String interest rate
    (150000, 0.1, "string", PaymentFrequency.MONTHLY, TypeError),  # ID: ERR-4: String period
], ids=["ERR-1", "ERR-2", "ERR-3", "ERR-4"])
def test_calculate_amortization_amount_error_cases(principal, interest_rate, period, payment_frequency, exception):
    # Act / Assert
    with pytest.raises(exception):
        calculate_amortization_amount(principal, interest_rate, period, payment_frequency)
