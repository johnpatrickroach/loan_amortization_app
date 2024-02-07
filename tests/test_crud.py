from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session, sessionmaker

from api.crud import create_loan_for_user, create_user, get_loan_schedule, get_loan_summary, get_user, \
    get_user_by_email, get_user_loans, \
    get_users, share_loan
from api.enums import PaymentFrequency
from api.models import Base, Loan, User
from api.schemas import LoanSchedule, UserCreate
from tests.factories import LoanCreateFactory, UserFactory


# Fixture to mock the database session
@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)


@pytest.mark.parametrize(
    "user_id, expected_user",
    [
        (1, User(id=1, email="test@test.com")),  # Test ID: Happy-Path-1
        (2, User(id=2, email="test2@test.com")),  # Test ID: Happy-Path-2
        (999, None),  # Test ID: Edge-Case-User-Not-Found
    ],
    ids=["Happy-Path-1", "Happy-Path-2", "Edge-Case-User-Not-Found"]
)
def test_get_user_happy_path_and_edge_case(mock_db_session, user_id, expected_user):
    # Arrange
    mock_db_session.query.return_value.filter.return_value.first.return_value = expected_user

    # Act
    result = get_user(mock_db_session, user_id)

    # Assert
    mock_db_session.query.assert_called_once_with(User)
    mock_db_session.query.return_value.filter.assert_called_once()
    assert result == expected_user, f"Expected {expected_user}, got {result}"


@pytest.mark.parametrize(
    "exception, status_code, detail",
    [
        (NoResultFound(), 404, "User not found"),  # Test ID: Error-Case-NoResultFound
        (Exception(), 500, "Internal Server Error"),  # Test ID: Error-Case-Exception
    ],
    ids=["Error-Case-NoResultFound", "Error-Case-Exception"]
)
def test_get_user_error_cases(mock_db_session, exception, status_code, detail):
    # Arrange
    mock_db_session.query.return_value.filter.return_value.first.side_effect = exception

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_user(mock_db_session, 1)
    assert exc_info.value.status_code == status_code, (f"Expected status code {status_code}, "
                                                       f"got {exc_info.value.status_code}")
    assert exc_info.value.detail == detail, f"Expected detail '{detail}', got '{exc_info.value.detail}'"


# Parametrized test for happy path scenarios
@pytest.mark.parametrize("email, user_id", [
    ("test@example.com", 1),
    ("another@example.com", 2),
])
def test_get_user_by_email_happy_path(mock_db_session, email, user_id):
    # Arrange
    expected_user = User(id=user_id, email=email)
    mock_db_session.query.return_value.filter.return_value.first.return_value = expected_user

    # Act
    result = get_user_by_email(mock_db_session, email)

    # Assert
    assert result == expected_user
    mock_db_session.query.assert_called_with(User)
    mock_db_session.query.return_value.filter.assert_called()


# Parametrized test for edge cases
@pytest.mark.parametrize("email", [
    "",
    "not_an_email",
])
def test_get_user_by_email_edge_cases(mock_db_session, email):
    # Arrange
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    # Act
    result = get_user_by_email(mock_db_session, email)

    # Assert
    assert result is None


# Parametrized test for error cases
@pytest.mark.parametrize("exception, expected_status", [
    (NoResultFound(), 404),
    (Exception(), 500),
])
def test_get_user_by_email_error_cases(mock_db_session, exception, expected_status):
    # Arrange
    mock_db_session.query.return_value.filter.return_value.first.side_effect = exception

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_user_by_email(mock_db_session, "test@example.com")
    assert exc_info.value.status_code == expected_status


# Setup for the tests: creating an in-memory SQLite database and a session
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="module")
def db_session():
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def fill_db(db_session):
    # Pre-populate the database with some users for testing
    users = [User(email=f"user{i}@example.com", hashed_password=f"pass{i}") for i in range(1, 11)]
    db_session.add_all(users)
    db_session.commit()


@pytest.mark.parametrize("skip, limit, expected_count, test_id", [
    (0, 5, 5, "happy_path_5_users"),
    (5, 5, 5, "happy_path_skip_5"),
    (0, 10, 10, "happy_path_all_users"),
    (10, 5, 0, "edge_case_skip_all"),
    (0, 0, 0, "edge_case_no_limit"),
    (-1, 5, 5, "error_negative_skip"),
    (0, -1, 10, "error_negative_limit"),
])
def test_get_users(db_session, fill_db, skip, limit, expected_count, test_id):
    # Arrange - setup is handled by the fixtures

    # Act
    result = get_users(db_session, skip, limit)

    # Assert
    assert len(
        result) == expected_count, f"Test ID: {test_id} failed. Expected {expected_count} users, got {len(result)}."


@pytest.mark.parametrize(
    "email, password, test_id",
    [
        ("test@example.com", "strongpassword", "happy_path_1"),
        ("unique@example.com", "anotherStrongPassword123", "happy_path_2"),
        # Add more test cases as needed
    ]
)
def test_create_user_happy_path(db_session, email, password, test_id):
    # Arrange
    user_data = UserCreate(email=email, password=password)

    # Act
    created_user = create_user(db_session, user_data)

    # Assert
    assert created_user.email == email
    assert created_user.hashed_password == f"{password}notreallyhashed"
    assert db_session.query(User).filter_by(email=email).count() == 1


@pytest.mark.parametrize(
    "email, password, test_id",
    [
        ("", "password", "edge_case_empty_email"),
        ("test2@example.com", "", "edge_case_empty_password"),
        # Add more test cases as needed
    ]
)
def test_create_user_edge_cases(db_session, email, password, test_id):
    # Arrange
    user_data = UserCreate(email=email, password=password)

    # Act
    created_user = create_user(db_session, user_data)

    # Assert
    assert created_user.email == email
    assert created_user.hashed_password == f"{password}notreallyhashed"
    assert db_session.query(User).filter_by(email=email).count() == 1


# Parametrized test for happy path scenarios
@pytest.mark.parametrize(
    "user_id, skip, limit, expected_loan_count, test_id",
    [
        (1, 0, 100, 5, "happy_path_default_skip_limit"),
        (2, 2, 50, 3, "happy_path_custom_skip_limit"),
        (3, 0, 1, 1, "happy_path_single_loan"),
    ]
)
def test_get_user_loans_happy_path(mock_db_session, user_id, skip, limit, expected_loan_count, test_id):
    # Arrange
    mock_user = MagicMock(spec=User)
    mock_user.id = user_id
    mock_loans = [MagicMock(spec=Loan) for _ in range(expected_loan_count)]
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    mock_db_session.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = (
        mock_loans)

    # Act
    result = get_user_loans(user_id, mock_db_session, skip, limit)

    # Assert
    assert len(
        result) == expected_loan_count, f"Test ID: {test_id} - Expected {expected_loan_count} loans, got {len(result)}"


# Parametrized test for error cases
@pytest.mark.parametrize(
    "user_id, test_id",
    [
        (99, "user_not_found"),
    ]
)
def test_get_user_loans_user_not_found(mock_db_session, user_id, test_id):
    # Arrange
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_user_loans(user_id, mock_db_session)
    assert exc_info.value.status_code == 404, (f"Test ID: {test_id} - Expected status code 404, "
                                               f"got {exc_info.value.status_code}")
    assert "User not found" in str(
        exc_info.value.detail), f"Test ID: {test_id} - Expected 'User not found' in error detail"


# Parametrized test for edge cases
@pytest.mark.parametrize(
    "user_id, skip, limit, expected_loan_count, test_id",
    [
        (1, 100, 0, 0, "edge_case_no_loans_due_to_skip"),
        (2, 0, 0, 0, "edge_case_no_loans_due_to_limit"),
    ]
)
def test_get_user_loans_edge_cases(mock_db_session, user_id, skip, limit, expected_loan_count, test_id):
    # Arrange
    mock_user = MagicMock(spec=User)
    mock_user.id = user_id
    mock_loans = [MagicMock(spec=Loan) for _ in range(expected_loan_count)]
    mock_db_session.query.return_value.filter.return_value.first.return_value = mock_user
    mock_db_session.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = (
        mock_loans)

    # Act
    result = get_user_loans(user_id, mock_db_session, skip, limit)

    # Assert
    assert len(
        result) == expected_loan_count, f"Test ID: {test_id} - Expected {expected_loan_count} loans, got {len(result)}"


@pytest.fixture
def user_factory():
    return UserFactory


@pytest.fixture
def loan_create_factory():
    return LoanCreateFactory


@pytest.mark.parametrize(
    "user_data, loan_data, test_id",
    [
        ({"email": "alice@example.com", "hashed_password": "password123"},
         {"amount": 10000, "annual_interest_rate": 5.0, "loan_term_months": 12, "frequency": 52}, "happy_path_1"),
        ({"email": "bob@example.com", "hashed_password": "password456"},
         {"amount": 5000, "annual_interest_rate": 3.0, "loan_term_months": 6, "frequency": 24}, "happy_path_2"),
        ({"email": "charlie@example.com", "hashed_password": "password789"},
         {"amount": 15000, "annual_interest_rate": 7.0, "loan_term_months": 24, "frequency": 12}, "happy_path_3"),
    ],
    ids=["happy_path_1", "happy_path_2", "happy_path_3"]
)
def test_create_loan_for_user_happy_path(mock_db_session: Session, user_factory, loan_create_factory, user_data,
                                         loan_data, test_id):
    # Arrange
    user = user_factory.create(**user_data)
    mock_db_session.add(user)
    mock_db_session.commit()
    loan_create = loan_create_factory.create(**loan_data)

    # Act
    created_loan = create_loan_for_user(mock_db_session, loan_create, user.id)

    # Assert
    assert created_loan.user_id == user.id
    assert created_loan.amount == loan_data["amount"]
    assert created_loan.annual_interest_rate == loan_data["annual_interest_rate"]
    assert created_loan.loan_term_months == loan_data["loan_term_months"]
    assert created_loan.frequency == loan_data["frequency"]


@pytest.mark.parametrize(
    "user_id, loan_data, test_id",
    [
        (999, {"amount": 10000, "annual_interest_rate": 5.0, "loan_term_months": 12, "frequency": 52},
         "error_user_not_found"),
    ],
    ids=["error_user_not_found"]
)
def test_create_loan_for_user_error_cases(mock_db_session: Session, loan_create_factory, user_id, loan_data, test_id):
    # Arrange
    # noinspection PyUnresolvedReferences
    mock_db_session.query.return_value.filter.return_value.first.return_value = None
    loan_create = loan_create_factory.create(**loan_data)

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        create_loan_for_user(mock_db_session, loan_create, user_id)
    assert exc_info.value.status_code == 404
    assert "User not found" in str(exc_info.value.detail)


# Mocking the database session and the Loan model
# noinspection PyAttributeOutsideInit
class FakeDBSession(Session):
    def query(self, model):
        self.model = model
        return self

    def filter(self, condition):
        self.condition = condition
        return self

    def first(self):
        # Mocking a Loan object based on the condition
        if self.condition.right.value == 1:  # Assuming loan_id == 1 exists
            return Loan(id=1, amount=10000, annual_interest_rate=5, loan_term_months=12,
                        frequency=PaymentFrequency.MONTHLY)
        elif self.condition.right.value == 2:  # Assuming loan_id == 2 exists but with edge case values
            return Loan(id=2, amount=500, annual_interest_rate=0.01, loan_term_months=1,
                        frequency=PaymentFrequency.MONTHLY)
        else:
            return None


@pytest.mark.parametrize(
    "loan_id, expected_length, test_id",
    [
        (1, 12, "happy_path"),
        (2, 1, "edge_case_min_values"),
    ]
)
def test_get_loan_schedule_happy_and_edge_cases(loan_id, expected_length, test_id):
    # Arrange
    db = FakeDBSession()

    # Act
    result = get_loan_schedule(loan_id, db)

    # Assert
    assert isinstance(result, list), f"Test Failed: {test_id} - Result is not a list"
    assert len(result) == expected_length, f"Test Failed: {test_id} - Incorrect number of schedule entries"
    assert all(isinstance(item, LoanSchedule) for item in
               result), f"Test Failed: {test_id} - Not all items are LoanSchedule instances"


@pytest.mark.parametrize(
    "loan_id, test_id",
    [
        (999, "loan_not_found"),
    ]
)
def test_get_loan_schedule_error_cases(loan_id, test_id):
    # Arrange
    db = FakeDBSession()

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_loan_schedule(loan_id, db)
    assert exc_info.value.status_code == 404, f"Test Failed: {test_id} - Incorrect status code"
    assert "Loan not found" in str(exc_info.value.detail), f"Test Failed: {test_id} - Incorrect error message"


# Parametrized test for happy path scenarios
@pytest.mark.parametrize(
    "loan_id, month, loan_data, expected_summary, test_id",
    [
        (1, 12,
         Loan(id=1, amount=100000, annual_interest_rate=5, loan_term_months=360, frequency=PaymentFrequency.MONTHLY),
         {'current_principal_balance': 98524.66, 'aggregate_principal_paid': 1475.34,
          'aggregate_interest_paid': 4966.5}, "happy_path_1"),
        (2, 24,
         Loan(id=2, amount=50000, annual_interest_rate=3, loan_term_months=120, frequency=PaymentFrequency.MONTHLY),
         {'current_principal_balance': 41161.37, 'aggregate_principal_paid': 8838.63,
          'aggregate_interest_paid': 2748.57}, "happy_path_2"),
    ],
)
def test_get_loan_summary_happy_path(mock_db_session, loan_id, month, loan_data, expected_summary, test_id):
    # Arrange
    mock_db_session.query.return_value.filter.return_value.first.return_value = loan_data

    # Act
    result = get_loan_summary(loan_id, month, mock_db_session)

    # Assert
    assert result.current_principal_balance == expected_summary['current_principal_balance']
    assert result.aggregate_principal_paid == expected_summary['aggregate_principal_paid']
    assert result.aggregate_interest_paid == expected_summary['aggregate_interest_paid']


# Parametrized test for edge cases
@pytest.mark.parametrize(
    "loan_id, month, loan_data, test_id",
    [
        (1, 0,
         Loan(id=1, amount=100000, annual_interest_rate=5, loan_term_months=360, frequency=PaymentFrequency.MONTHLY),
         "edge_case_month_zero"),
        (2, 361,
         Loan(id=2, amount=50000, annual_interest_rate=3, loan_term_months=360, frequency=PaymentFrequency.MONTHLY),
         "edge_case_month_beyond_term"),
    ],
)
def test_get_loan_summary_edge_cases(mock_db_session, loan_id, month, loan_data, test_id):
    # Arrange
    mock_db_session.query.return_value.filter.return_value.first.return_value = loan_data

    # Act
    result = get_loan_summary(loan_id, month, mock_db_session)

    # Assert
    assert result is not None  # Specific assertions depend on the function's handling of edge cases


# Parametrized test for error cases
@pytest.mark.parametrize(
    "loan_id, month, test_id",
    [
        (999, 12, "error_case_loan_not_found"),
    ],
)
def test_get_loan_summary_error_cases(mock_db_session, loan_id, month, test_id):
    # Arrange
    mock_db_session.query.return_value.filter.return_value.first.return_value = None

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        get_loan_summary(loan_id, month, mock_db_session)
    assert exc_info.value.status_code == 404
    assert "Loan not found" in str(exc_info.value.detail)


# Parametrized test for the happy path with various realistic test values
@pytest.mark.parametrize(
    "loan_id, user_id, expected_message, test_id",
    [
        (1, 2, {"message": "Loan shared successfully"}, "happy_path_1"),
        (10, 20, {"message": "Loan shared successfully"}, "happy_path_2"),
        (100, 200, {"message": "Loan shared successfully"}, "happy_path_3"),
    ]
)
def test_share_loan_happy_path(mock_db_session, loan_id, user_id, expected_message, test_id):
    # Arrange
    mock_loan = Loan(id=loan_id)
    mock_user = User(id=user_id)
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [mock_loan, mock_user]

    # Act
    result = share_loan(loan_id, user_id, mock_db_session)

    # Assert
    mock_db_session.commit.assert_called_once()
    assert result == expected_message, f"Test ID: {test_id}"


# Parametrized test for various error cases
@pytest.mark.parametrize(
    "loan_id, user_id, first_return, second_return, expected_exception, test_id",
    [
        (1, 2, None, User(id=2), HTTPException, "error_loan_not_found"),
        (1, 2, Loan(id=1), None, HTTPException, "error_user_not_found"),
    ]
)
def test_share_loan_error_cases(mock_db_session, loan_id, user_id, first_return, second_return, expected_exception,
                                test_id):
    # Arrange
    mock_db_session.query.return_value.filter.return_value.first.side_effect = [first_return, second_return]

    # Act & Assert
    with pytest.raises(expected_exception) as exc_info:
        share_loan(loan_id, user_id, mock_db_session)
    assert exc_info.value.status_code == 404, f"Test ID: {test_id}"
