from sqlalchemy import Boolean, Column, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from api.database import Base
from api.enums import PaymentFrequency


class User(Base):
    """
    Model representing a user.

    Explanation:
    This class defines a user model with attributes such as id, email, hashed_password, and is_active.
    It also establishes a relationship with the Loan model.

    Args:
        - No arguments required for class methods.

    Attributes:
        - id (int): The primary key of the user.
        - email (str): The email address of the user.
        - hashed_password (str): The hashed password of the user.
        - is_active (bool): Indicates whether the user is active or not.
        - loans (relationship): A relationship to the Loan model.

    Returns:
        - No return value for class methods.

    Raises:
        - No exceptions raised for class methods.

    Examples:
        - No examples provided for a class.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True, nullable=False)
    # username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    loans = relationship("Loan", back_populates="user")


class Loan(Base):
    """
    Model representing a loan.

    Explanation:
    This class defines a loan model with attributes such as id, amount, annual_interest_rate, loan_term_months,
        frequency, and user_id.
    It also establishes a relationship with the User model.

    Args:
        - No arguments required for class methods.

    Attributes:
        - id (int): The primary key of the loan.
        - amount (float): The amount of the loan.
        - annual_interest_rate (float): The annual interest rate of the loan.
        - loan_term_months (int): The loan term in months.
        - frequency (enum): The payment frequency of the loan.
        - user_id (int): The foreign key referencing the user.

    Returns:
        - No return value for class methods.

    Raises:
        - No exceptions raised for class methods.

    Examples:
        - No examples provided for a class.
    """

    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float)
    annual_interest_rate = Column(Float)
    loan_term_months = Column(Integer)
    frequency = Column(Enum(PaymentFrequency))
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="loans")
