from typing import Type

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from api.crud import (
    create_loan_for_user,
    create_user,
    get_loan_schedule,
    get_loan_summary,
    get_users,
    get_user_by_email,
    get_user_loans,
    share_loan
)
from api.database import SessionLocal, engine
from api.models import Base
from api.schemas import Loan, LoanCreate, LoanSchedule, LoanSummary, User, UserCreate


# Create FastAPI instance
app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)


# Dependency to get DB session
def get_db() -> Session:
    """
    Get a database session.

    Explanation:
    This function returns a database session using a context manager.
    It yields the session object, allowing it to be used within a 'with' statement.
    After the 'with' block is executed, the session is closed.

    Args:
        - No arguments required.

    Yields:
        - Session: The database session object.

    Raises:
        - HTTPException: If there is an error while creating the database session.

    Examples:
        - No examples provided for a function.
    """
    db = None
    try:
        db: Session | None = SessionLocal()
        yield db
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error") from e
    finally:
        if db:
            db.close()


# Define endpoints
@app.get("/")
def index() -> dict:
    """
    Handle the index route.

    Explanation:
    This function handles the index route ("/") and returns a simple JSON response.

    Args:
        - No arguments required.

    Returns:
        - dict: A dictionary representing the JSON response.

    Raises:
        - No exceptions raised by this function.

    Examples:
        - No examples provided for a function.
    """
    return {"msg": "Hello World"}


@app.get("/users/", response_model=list[User])
def get_users_endpoint(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)) -> list[Type[User]]:
    """
    Retrieve multiple users from the database.

    Explanation:
    This function handles the GET request to the "/users/" endpoint and retrieves multiple users from the database.
    It delegates the actual retrieval to the get_users function, passing the provided skip and limit parameters.

    Args:
        - skip (int): The number of users to skip. Defaults to 0.
        - limit (int): The maximum number of users to retrieve. Defaults to 100.
        - db (Session): The database session object.

    Returns:
        - List[User]: A list of user objects retrieved from the database.

    Raises:
        - No exceptions raised by this function.

    Examples:
        - No examples provided for a function.
    """
    return get_users(db=db, skip=skip, limit=limit)


@app.post("/users/", response_model=User)
def create_user_endpoint(user: UserCreate, db: Session = Depends(get_db)) -> User:
    """
    Create a new user.

    Explanation:
    This function handles the POST request to the "/users/" endpoint and creates a new user.
    It first checks if a user with the provided email already exists in the database.
    If a user with the same email is found, it raises an HTTPException with a status code of 400.
    Otherwise, it creates a new user using the provided UserCreate object and returns the created user.

    Args:
        - user (UserCreate): The UserCreate object containing the user details.
        - db (Session): The database session object.

    Returns:
        - User: The newly created user object.

    Raises:
        - HTTPException: If a user with the same email already exists in the database.

    Examples:
        - No examples provided for a function.
    """
    if db_user := get_user_by_email(db, email=user.email):
        raise HTTPException(status_code=400, detail=f"Email {db_user.email} already registered")
    return create_user(db=db, user=user)


@app.post("/users/{user_id}/loans/", response_model=Loan)
def create_loan_for_user_endpoint(
    user_id: int,
    loan: LoanCreate,
    db: Session = Depends(get_db)
) -> Loan:
    """
    Create a loan for a specific user.

    Explanation:
    This function handles the POST request to the "/users/{user_id}/loans/" endpoint and creates a new loan for a
        specific user.
    It first retrieves the user from the database based on the provided user_id.
    If the user is found, it creates a new loan using the provided LoanCreate object and the user_id.
    The loan is then returned.

    Args:
        - user_id (int): The ID of the user.
        - loan (LoanCreate): The LoanCreate object containing the loan details.
        - db (Session): The database session object.

    Returns:
        - Loan: The newly created loan object.

    Raises:
        - No exceptions raised by this function.

    Examples:
        - No examples provided for a function.
    """
    return create_loan_for_user(db=db, loan=loan, user_id=user_id)


@app.get("/users/{user_id}/loans/", response_model=list[Loan])
def get_user_loans_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
) -> list[Loan]:
    """
    Get the loans for a specific user.

    Args:
        user_id (int): The ID of the user.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to retrieve. Defaults to 100.

    Returns:
        list[Loan]: A list of Loan objects representing the user's loans.

    Examples:
        >>> get_user_loans_endpoint(1)
        [Loan(id=1, amount=1000.0, interest_rate=0.05), Loan(id=2, amount=2000.0, interest_rate=0.1)]
    """
    return get_user_loans(user_id=user_id, db=db, skip=skip, limit=limit)


@app.get("/loans/{loan_id}/schedule/", response_model=list[LoanSchedule])
def get_loan_schedule_endpoint(loan_id: int, db: Session = Depends(get_db)) -> list[LoanSchedule]:
    """
    Get the repayment schedule for a specific loan.

    Args:
        loan_id (int): The ID of the loan.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        list[LoanSchedule]: A list of LoanSchedule objects representing the repayment schedule for the loan.
    """
    return get_loan_schedule(loan_id=loan_id, db=db)


@app.get("/loans/{loan_id}/summary/{month}/", response_model=LoanSummary)
def get_loan_summary_endpoint(loan_id: int, month: int, db: Session = Depends(get_db)) -> LoanSummary:
    """
    Get the summary of a specific loan for a given month.

    Args:
        loan_id (int): The ID of the loan.
        month (int): The month for which to retrieve the loan summary.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        LoanSummary: An object representing the summary of the loan for the given month.
    """
    return get_loan_summary(loan_id=loan_id, month=month, db=db)


@app.post("/loans/{loan_id}/share/")
def share_loan_endpoint(loan_id: int, user_id: int, db: Session = Depends(get_db)) -> dict:
    """
    Share a specific loan with another user.

    Args:
        loan_id (int): The ID of the loan to share.
        user_id (int): The ID of the user to share the loan with.
        db (Session, optional): The database session. Defaults to Depends(get_db).

    Returns:
        dict

    Raises:
        HTTPException: If the loan or user does not exist, or if there is an error sharing the loan.
    """
    return share_loan(loan_id=loan_id, user_id=user_id, db=db)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
