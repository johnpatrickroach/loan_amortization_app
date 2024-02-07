import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from api.models import User, Base

# Setup for the database session
DATABASE_URL = "sqlite://"
engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


# Fixture to create a new database session
@pytest.fixture(scope="function")
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()


# Parametrized test for the happy path
@pytest.mark.parametrize(
    "test_id, email, hashed_password, is_active",
    [
        ("happy-1", "user@example.com", "hashedpassword123", True),
        ("happy-2", "anotheruser@example.com", "diffhashpass456", False),
        # Add more test cases with realistic values
    ]
)
def test_create_user_happy_path(db_session, test_id, email, hashed_password, is_active):
    # Arrange
    new_user = User(email=email, hashed_password=hashed_password, is_active=is_active)

    # Act
    db_session.add(new_user)
    db_session.commit()

    # Assert
    assert new_user.id is not None
    assert new_user.email == email
    assert new_user.hashed_password == hashed_password
    assert new_user.is_active == is_active


# Parametrized test for edge cases
@pytest.mark.parametrize(
    "test_id, email, hashed_password, is_active",
    [
        ("edge-1", "", "hashedpassword123", True),  # Empty email
        ("edge-2", "user@example.com", "", True),   # Empty password
        # Add more edge cases
    ]
)
def test_create_user_edge_cases(db_session, test_id, email, hashed_password, is_active):
    # Arrange
    new_user = User(email=email, hashed_password=hashed_password, is_active=is_active)

    # Act
    db_session.add(new_user)
    db_session.commit()

    # Assert
    assert new_user.id is not None
    assert new_user.email == email
    assert new_user.hashed_password == hashed_password
    assert new_user.is_active == is_active


# Parametrized test for error cases
@pytest.mark.parametrize(
    "test_id, email, hashed_password, is_active",
    [
        ("error-1", None, "hashedpassword123", True),  # None email
        ("error-2", "user@example.com", None, True),   # None password
        # Add more error cases
    ]
)
def test_create_user_error_cases(db_session, test_id, email, hashed_password, is_active):
    # Arrange
    new_user = User(email=email, hashed_password=hashed_password, is_active=is_active)

    with pytest.raises(IntegrityError):
        # Act
        db_session.add(new_user)
        db_session.commit()

        # Assert
        assert new_user.id is None
