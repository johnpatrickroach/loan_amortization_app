# Description: This file contains the utility functions for the application.
from typing import Iterator, Tuple

from api.enums import PaymentFrequency


def calculate_amortization_amount(
    principal: float, interest_rate: float, period: int, payment_frequency: PaymentFrequency = PaymentFrequency.MONTHLY
) -> float:
    """
    Calculates Amortization Amount per period

    >>> calculate_amortization_amount(150000, 0.1, 36)
    4840.08

    >>> calculate_amortization_amount(150000, 0.1, 36, PaymentFrequency.SEMIMONTHLY)
    4495.63

    :param principal: Principal amount
    :param interest_rate: Interest rate per year
    :param period: Total number of period
    :param payment_frequency: Payment frequency per year
    :return: Amortization amount per period
    """
    adjusted_interest: float = interest_rate / payment_frequency.value
    x: float = (1 + adjusted_interest) ** period
    return round(principal * (adjusted_interest * x) / (x - 1), 2)


def amortization_schedule(
    principal: float, interest_rate: float, period: int, payment_frequency: PaymentFrequency = PaymentFrequency.MONTHLY
) -> Iterator[Tuple[int, float, float, float, float]]:
    """
    Generates amortization schedule

    :param principal: Principal amount
    :param interest_rate: Interest rate per year
    :param period: Total number of periods
    :param payment_frequency: Payment frequency per year
    :return: Rows containing period, amount, interest, principal, balance, etc
    """
    amortization_amount: float = calculate_amortization_amount(principal, interest_rate, period, payment_frequency)
    adjusted_interest: float = interest_rate / payment_frequency.value
    balance: float = principal
    for number in range(1, period):
        interest = round(balance * adjusted_interest, 2)
        principal_payment = amortization_amount - interest
        balance -= principal_payment
        yield number, amortization_amount, interest, principal_payment, balance
    interest = round(balance * adjusted_interest, 2)
    yield period, balance + interest, interest, balance, 0
