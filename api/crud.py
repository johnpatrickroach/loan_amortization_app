from typing import Type

from fastapi import HTTPException
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from api.models import Loan, User
from api.schemas import LoanCreate, LoanSchedule, LoanSummary, UserCreate
from api.utils import amortization_schedule


# noinspection PyTypeChecker
def get_user(db: Session, user_id: int) -> User:
    """
    Retrieve a user from the database by user ID.

    Explanation:
    This function queries the database to retrieve a user based on the provided user ID.
    It returns the first user that matches the given ID, or None if no user is found.

    Args:
        - db (Session): The database session object.
        - user_id (int): The ID of the user to retrieve.

    Returns:
        - User: The user object retrieved from the database, or None if no user is found.

    Raises:
        - HTTPException: If there is an error while retrieving the user.

    Examples:
        - No examples provided for a function.
    """
    try:
        return db.query(User).filter(User.id == user_id).first()
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail="User not found") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


# noinspection PyTypeChecker
def get_user_by_email(db: Session, email: str) -> User:
    """
    Retrieve a user from the database by email.

    Explanation:
    This function queries the database to retrieve a user based on the provided email address.
    It returns the first user that matches the given email, or None if no user is found.

    Args:
        - db (Session): The database session object.
        - email (str): The email address of the user to retrieve.

    Returns:
        - User: The user object retrieved from the database, or None if no user is found.

    Raises:
        - HTTPException: If there is an error while retrieving the user.

    Examples:
        - No examples provided for a function.
    """
    try:
        return db.query(User).filter(User.email == email).first()
    except NoResultFound as e:
        raise HTTPException(status_code=404, detail="User not found") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


def get_users(db: Session, skip: int = 0, limit: int = 100) -> list[Type[User]]:
    """
    Retrieve multiple users from the database.

    Explanation:
    This function queries the database to retrieve multiple users.
    It allows for pagination by specifying the number of users to skip and the maximum number of users to retrieve.

    Args:
        - db (Session): The database session object.
        - skip (int): The number of users to skip. Defaults to 0.
        - limit (int): The maximum number of users to retrieve. Defaults to 100.

    Returns:
        - List[User]: A list of user objects retrieved from the database.

    Raises:
        - No exceptions raised by this function.

    Examples:
        - No examples provided for a function.
    """
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user in the database.

    Explanation:
    This function creates a new user in the database based on the provided UserCreate object.
    It generates a fake hashed password, initializes a new User object, adds it to the database session,
    commits the changes, refreshes the user object, and returns it.

    Args:
        - db (Session): The database session object.
        - user (UserCreate): The UserCreate object containing the user details.

    Returns:
        - User: The newly created user object.

    Raises:
        - No exceptions raised by this function.

    Examples:
        - No examples provided for a function.
    """
    fake_hashed_password: str = f"{user.password}notreallyhashed"
    db_user: User = User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# noinspection PyTypeChecker
def get_user_loans(user_id: int, db: Session, skip: int = 0, limit: int = 100) -> list[Loan]:
    """
    Retrieve loans for a specific user from the database.

    Explanation:
    This function queries the database to retrieve loans associated with a specific user.
    It first checks if the user with the given user_id exists in the database.
    If the user is found, it retrieves the loans associated with that user based on the provided skip and limit
        parameters.
    If the user is not found, it raises an HTTPException with a status code of 404.

    Args:
        - user_id (int): The ID of the user.
        - db (Session): The database session object.
        - skip (int): The number of loans to skip. Defaults to 0.
        - limit (int): The maximum number of loans to retrieve. Defaults to 100.

    Returns:
        - List[Loan]: A list of loan objects associated with the user.

    Raises:
        - HTTPException: If the user with the given user_id is not found in the database.

    Examples:
        - No examples provided for a function.
    """
    if db_user := db.query(User).filter(User.id == user_id).first():
        return db.query(Loan).filter(Loan.user_id == db_user.id).offset(skip).limit(limit).all()
    else:
        raise HTTPException(status_code=404, detail="User not found")


# noinspection PyTypeChecker
def create_loan_for_user(db: Session, loan: LoanCreate, user_id: int) -> Loan:
    """
    Create a loan for a specific user in the database.

    Explanation:
    This function creates a new loan in the database for a specific user.
    It first checks if the user with the given user_id exists in the database.
    If the user is found, it creates a new Loan object based on the provided LoanCreate object and user_id.
    It adds the loan to the database session, commits the changes, refreshes the loan object, and returns it.
    If the user is not found, it raises an HTTPException with a status code of 404.

    Args:
        - db (Session): The database session object.
        - loan (LoanCreate): The LoanCreate object containing the loan details.
        - user_id (int): The ID of the user.

    Returns:
        - Loan: The newly created loan object.

    Raises:
        - HTTPException: If the user with the given user_id is not found in the database.

    Examples:
        - No examples provided for a function.
    """
    db_user: User = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_loan: Loan = Loan(**loan.dict(), user_id=user_id)
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan


# noinspection PyTypeChecker
def get_loan_schedule(loan_id: int, db: Session) -> list[LoanSchedule]:
    """
    Retrieve the loan schedule for a specific loan from the database.

    Explanation:
    This function queries the database to retrieve the loan schedule for a specific loan based on the provided loan_id.
    It calculates the amortization schedule using the loan details, such as the principal amount, interest rate, loan
        term, and payment frequency.
    It then constructs a list of LoanSchedule objects representing each month's details in the amortization schedule.
    If the loan is not found, it raises an HTTPException with a status code of 404.

    Args:
        - loan_id (int): The ID of the loan.
        - db (Session): The database session object.

    Returns:
        - List[LoanSchedule]: A list of LoanSchedule objects representing the loan schedule.

    Raises:
        - HTTPException: If the loan with the given loan_id is not found in the database.

    Examples:
        - No examples provided for a function.
    """
    if db_loan := db.query(Loan).filter(Loan.id == loan_id).first():
        amortization_data: list = list(
            amortization_schedule(
                principal=db_loan.amount,
                interest_rate=db_loan.annual_interest_rate / 100,
                period=db_loan.loan_term_months,
                payment_frequency=db_loan.frequency,
            )
        )
        return [
            LoanSchedule(
                month=month,
                remaining_balance=round(balance, 2),
                monthly_payment=round(amortization_amount, 2),
                # interest=round(interest, 2),
                # principal=round(principal, 2),

            )
            for month, amortization_amount, interest, principal, balance in amortization_data
        ]
    else:
        raise HTTPException(status_code=404, detail="Loan not found")


# noinspection PyTypeChecker
def get_loan_summary(loan_id: int, month: int, db: Session) -> LoanSummary:
    """
    Retrieve the loan summary for a specific loan up to a given month from the database.

    Explanation:
    This function queries the database to retrieve the loan summary for a specific loan based on the provided loan_id
        and month.
    It calculates the amortization schedule using the loan details, such as the principal amount, interest rate, loan
        term, and payment frequency.
    It then calculates the current principal balance, aggregate principal paid, and aggregate interest paid up to the
        given month.
    The loan summary is returned as a LoanSummary object.
    If the loan is not found, it raises an HTTPException with a status code of 404.

    Args:
        - loan_id (int): The ID of the loan.
        - month (int): The month up to which the loan summary should be calculated.
        - db (Session): The database session object.

    Returns:
        - LoanSummary: The loan summary object representing the loan summary up to the given month.

    Raises:
        - HTTPException: If the loan with the given loan_id is not found in the database.

    Examples:
        - No examples provided for a function.
    """
    db_loan: Loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not db_loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    amortization_data: list = list(
        amortization_schedule(
            principal=db_loan.amount,
            interest_rate=db_loan.annual_interest_rate / 100,
            period=db_loan.loan_term_months,
            payment_frequency=db_loan.frequency,
        )
    )

    current_principal_balance: float = 0
    aggregate_principal_paid: float = 0
    aggregate_interest_paid: float = 0

    for month_data in amortization_data[:month]:
        current_principal_balance = month_data[4]
        aggregate_principal_paid += month_data[3]
        aggregate_interest_paid += month_data[2]

    return LoanSummary(
        current_principal_balance=round(current_principal_balance, 2),
        aggregate_principal_paid=round(aggregate_principal_paid, 2),
        aggregate_interest_paid=round(aggregate_interest_paid, 2),
    )


# noinspection PyTypeChecker
def share_loan(loan_id: int, user_id: int, db: Session) -> dict:
    """
    Share a loan with another user.

    Explanation:
    This function allows sharing a loan with another user by assigning the loan to the specified user.
    It retrieves the loan and user from the database based on the provided loan_id and user_id.
    If the loan or user is not found, it raises an HTTPException with a status code of 404.
    If the loan and user are found, the loan is assigned to the user and the changes are committed to the database.

    Args:
        - loan_id (int): The ID of the loan to be shared.
        - user_id (int): The ID of the user with whom the loan is to be shared.
        - db (Session): The database session object.

    Returns:
        - dict: A dictionary with a message indicating the successful sharing of the loan.

    Raises:
        - HTTPException: If the loan or user with the given IDs are not found in the database.

    Examples:
        - No examples provided for a function.
    """
    # Retrieve the loan from the database
    loan: Loan = db.query(Loan).filter(Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    # Retrieve the user with whom the loan is to be shared
    user_to_share: User = db.query(User).filter(User.id == user_id).first()
    if not user_to_share:
        raise HTTPException(status_code=404, detail="User not found")

    # Assign the loan to the user
    loan.user_id = user_to_share.id
    db.commit()

    return {"message": "Loan shared successfully"}
