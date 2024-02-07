import pytest
from api.enums import PaymentFrequency

# Define a list of tuples containing enum members and their expected values
payment_frequencies = [
    (PaymentFrequency.DAILY, 365, "test_daily"),
    (PaymentFrequency.BIWEEKLY, 104, "test_biweekly"),
    (PaymentFrequency.WEEKLY, 52, "test_weekly"),
    (PaymentFrequency.SEMIMONTHLY, 24, "test_semimonthly"),
    (PaymentFrequency.MONTHLY, 12, "test_monthly"),
    (PaymentFrequency.QUARTERLY, 4, "test_quarterly"),
    (PaymentFrequency.SEMIYEARLY, 2, "test_semiyearly"),
    (PaymentFrequency.YEARLY, 1, "test_yearly"),
]


@pytest.mark.parametrize("frequency, expected_value, test_id", payment_frequencies)
def test_payment_frequency_values(frequency, expected_value, test_id):
    # Assert
    assert frequency == expected_value, f"{test_id}: The value of {frequency} should be {expected_value}"
