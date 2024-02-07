import pytest

from api.enums import PaymentFrequency
from api.schemas import Loan, LoanCreate, LoanSchedule, LoanSummary


# Happy path tests with various realistic test values
@pytest.mark.parametrize(
    "test_id, amount, annual_interest_rate, loan_term_months, frequency",
    [
        ("HP_01", 10000.0, 5.0, 120, PaymentFrequency.MONTHLY),
        ("HP_02", 50000.0, 3.5, 240, PaymentFrequency.BIWEEKLY),
        ("HP_03", 75000.0, 4.0, 360, PaymentFrequency.YEARLY),
    ]
)
def test_loan_create_happy_path(test_id, amount, annual_interest_rate, loan_term_months, frequency):
    # Act
    loan = LoanCreate(
        amount=amount,
        annual_interest_rate=annual_interest_rate,
        loan_term_months=loan_term_months,
        frequency=frequency
    )

    # Assert
    assert loan.amount == amount
    assert loan.annual_interest_rate == annual_interest_rate
    assert loan.loan_term_months == loan_term_months
    assert loan.frequency == frequency


# Edge cases
@pytest.mark.parametrize(
    "test_id, amount, annual_interest_rate, loan_term_months, frequency",
    [
        ("EC_01", 0.01, 0.0, 1, PaymentFrequency.MONTHLY),
        ("EC_02", 1000000.0, 0.0, 1, PaymentFrequency.MONTHLY),
        ("EC_03", 10000.0, 99.99, 480, PaymentFrequency.YEARLY),
    ]
)
def test_loan_create_edge_cases(test_id, amount, annual_interest_rate, loan_term_months, frequency):
    # Act
    loan = LoanCreate(
        amount=amount,
        annual_interest_rate=annual_interest_rate,
        loan_term_months=loan_term_months,
        frequency=frequency
    )

    # Assert
    assert loan.amount == amount
    assert loan.annual_interest_rate == annual_interest_rate
    assert loan.loan_term_months == loan_term_months
    assert loan.frequency == frequency


# Error cases
@pytest.mark.parametrize(
    "test_id, amount, annual_interest_rate, loan_term_months, frequency, expected_exception",
    [
        ("ERR_01", -10000.0, "five", 120, PaymentFrequency.MONTHLY, ValueError),
        ("ERR_02", 10000.0, " negative one", 120, PaymentFrequency.MONTHLY, ValueError),
        ("ERR_03", 10000.0, 5.0, "zero", PaymentFrequency.MONTHLY, ValueError),
        ("ERR_04", 10000.0, 5.0, 120, "InvalidFrequency", ValueError),
    ]
)
def test_loan_create_error_cases(test_id, amount, annual_interest_rate, loan_term_months, frequency,
                                 expected_exception):
    # Act and Assert
    with pytest.raises(expected_exception):
        LoanCreate(
            amount=amount,
            annual_interest_rate=annual_interest_rate,
            loan_term_months=loan_term_months,
            frequency=frequency
        )


# Test IDs for different scenarios
happy_path_ids = [
    "positive_ids",
    "max_int_values"
]

edge_case_ids = [
    "zero_ids"
]

error_case_ids = [
    "non_int_id",
    "non_int_user_id"
]


# Happy path test values
@pytest.mark.parametrize("loan_id, user_id", [
    (1, 100),  # positive_ids
    (2147483647, 2147483647)  # max_int_values
], ids=happy_path_ids)
def test_loan_happy_path(loan_id, user_id):
    # Act
    loan = Loan(id=loan_id, user_id=user_id)

    # Assert
    assert loan.id == loan_id, "The loan ID should match the provided loan_id"
    assert loan.user_id == user_id, "The user ID should match the provided user_id"


# Edge case test values
@pytest.mark.parametrize("loan_id, user_id", [
    (0, 0)  # zero_ids
], ids=edge_case_ids)
def test_loan_edge_cases(loan_id, user_id):
    # Act
    loan = Loan(id=loan_id, user_id=user_id)

    # Assert
    assert loan.id == loan_id, "The loan ID should be zero"
    assert loan.user_id == user_id, "The user ID should be zero"


# Error case test values
@pytest.mark.parametrize("loan_id, user_id", [
    ("one", 1),  # non_int_id
    (1, "one")  # non_int_id
], ids=error_case_ids)
def test_loan_error_cases(loan_id, user_id):
    # Act & Assert
    with pytest.raises(ValueError):
        Loan(id=loan_id, user_id=user_id)


# Happy path tests with various realistic test values
@pytest.mark.parametrize(
    "test_id, month, remaining_balance, monthly_payment",
    [
        ("HP_01", 1, 100000.0, 500.0),
        ("HP_02", 12, 95000.0, 500.0),
        ("HP_03", 24, 90000.0, 500.0),
        # Add more test cases as needed
    ],
)
def test_loan_schedule_happy_path(test_id, month, remaining_balance, monthly_payment):
    # Act
    loan_schedule = LoanSchedule(month=month, remaining_balance=remaining_balance, monthly_payment=monthly_payment)

    # Assert
    assert loan_schedule.month == month
    assert loan_schedule.remaining_balance == remaining_balance
    assert loan_schedule.monthly_payment == monthly_payment


# Edge cases
@pytest.mark.parametrize(
    "test_id, month, remaining_balance, monthly_payment",
    [
        ("EC_01", 0, 0.0, 0.0),  # Edge case with zero values
        ("EC_02", 1, 0.01, 0.01),  # Edge case with very small values
        # Add more test cases as needed
    ],
)
def test_loan_schedule_edge_cases(test_id, month, remaining_balance, monthly_payment):
    # Act
    loan_schedule = LoanSchedule(month=month, remaining_balance=remaining_balance, monthly_payment=monthly_payment)

    # Assert
    assert loan_schedule.month == month
    assert loan_schedule.remaining_balance == remaining_balance
    assert loan_schedule.monthly_payment == monthly_payment


# Error cases
@pytest.mark.parametrize(
    "test_id, month, remaining_balance, monthly_payment, expected_exception",
    [
        ("ERR_01", "one", 100000.0, 500.0, ValueError),  # Negative month
        ("ERR_02", 1, "onethousand", 500.0, ValueError),  # Negative remaining_balance
        ("ERR_03", 1, 100000.0, "fivehundred", ValueError),  # Negative monthly_payment
        # Add more test cases as needed
    ],
)
def test_loan_schedule_error_cases(test_id, month, remaining_balance, monthly_payment, expected_exception):
    # Act and Assert
    with pytest.raises(expected_exception):
        LoanSchedule(month=month, remaining_balance=remaining_balance, monthly_payment=monthly_payment)


# Test IDs for parametrization
HAPPY_PATH_ID = "happy"
EDGE_CASE_ID = "edge"
ERROR_CASE_ID = "error"

# Happy path test values
happy_path_test_values = [
    (100000.0, 50000.0, 20000.0, HAPPY_PATH_ID + "-1"),
    (0.0, 100000.0, 50000.0, HAPPY_PATH_ID + "-2"),
    (1.0, 0.0, 0.0, HAPPY_PATH_ID + "-3"),
]

# Edge case test values
edge_case_test_values = [
    (0.0, 0.0, 0.0, EDGE_CASE_ID + "-1"),
]

# Error case test values
error_case_test_values = [
    (None, 100000.0, 50000.0, ERROR_CASE_ID + "-1"),
    ("not-a-float", 50000.0, 20000.0, ERROR_CASE_ID + "-2"),
    (100000.0, "not-a-float", 20000.0, ERROR_CASE_ID + "-3"),
    (100000.0, 50000.0, "not-a-float", ERROR_CASE_ID + "-4"),
]


@pytest.mark.parametrize(
    "current_principal_balance, aggregate_principal_paid, aggregate_interest_paid, test_id",
    happy_path_test_values,
)
def test_loan_summary_happy_path(current_principal_balance, aggregate_principal_paid, aggregate_interest_paid, test_id):
    # Act
    loan_summary = LoanSummary(
        current_principal_balance=current_principal_balance,
        aggregate_principal_paid=aggregate_principal_paid,
        aggregate_interest_paid=aggregate_interest_paid
    )

    # Assert
    assert loan_summary.current_principal_balance == current_principal_balance
    assert loan_summary.aggregate_principal_paid == aggregate_principal_paid
    assert loan_summary.aggregate_interest_paid == aggregate_interest_paid


@pytest.mark.parametrize(
    "current_principal_balance, aggregate_principal_paid, aggregate_interest_paid, test_id",
    edge_case_test_values,
)
def test_loan_summary_edge_cases(current_principal_balance, aggregate_principal_paid, aggregate_interest_paid, test_id):
    # Act
    loan_summary = LoanSummary(
        current_principal_balance=current_principal_balance,
        aggregate_principal_paid=aggregate_principal_paid,
        aggregate_interest_paid=aggregate_interest_paid
    )

    # Assert
    assert loan_summary.current_principal_balance == current_principal_balance
    assert loan_summary.aggregate_principal_paid == aggregate_principal_paid
    assert loan_summary.aggregate_interest_paid == aggregate_interest_paid


@pytest.mark.parametrize(
    "current_principal_balance, aggregate_principal_paid, aggregate_interest_paid, test_id",
    error_case_test_values,
)
def test_loan_summary_error_cases(current_principal_balance, aggregate_principal_paid, aggregate_interest_paid,
                                  test_id):
    # Act & Assert
    with pytest.raises(ValueError):
        LoanSummary(
            current_principal_balance=current_principal_balance,
            aggregate_principal_paid=aggregate_principal_paid,
            aggregate_interest_paid=aggregate_interest_paid
        )
