from typing import Dict

from pydantic import BaseModel

from api.enums import PaymentFrequency


class LoanBase(BaseModel):
    """
    Base schema for a loan.

    Explanation:
    This class serves as the base schema for a loan, providing a foundation for defining loan-related schemas.
    It inherits from the BaseModel class.

    Args:
        - No arguments required for class methods.

    Returns:
        - No return value for class methods.

    Raises:
        - No exceptions raised for class methods.

    Examples:
        - No examples provided for a class.
    """
    pass


class LoanCreate(LoanBase):
    """
    Schema for creating a loan.

    Explanation:
    This class defines a schema for creating a loan, specifying the required fields and their constraints.
    It inherits from the LoanBase schema.

    Args:
        - amount (float): Loan amount in dollars. Must be greater than 0.
        - annual_interest_rate (float): Annual interest rate in percentage. Must be greater than or equal to 0.
        - loan_term_months (int): Loan term in months. Must be greater than 0.
        - frequency (PaymentFrequency): Payment frequency in months.

    Returns:
        - No return value for class methods.

    Raises:
        - No exceptions raised for class methods.

    Examples:
        - No examples provided for a class.
    """
    amount: float
    annual_interest_rate: float
    loan_term_months: int
    frequency: PaymentFrequency


class Loan(LoanBase):
    """
    Model representing a loan.

    Explanation:
    This class defines a loan model with attributes id and user_id.
    It inherits from the LoanBase class and includes a configuration class for attribute initialization.

    Args:
        - id (int): The ID of the loan.
        - user_id (int): The ID of the user associated with the loan.

    Returns:
        - No return value for class methods.

    Raises:
        - No exceptions raised for class methods.

    Examples:
        - No examples provided for a class.
    """

    id: int
    user_id: int

    class Config:
        from_attributes = True


class LoanSchedule(BaseModel):
    """
    Model representing a loan schedule.

    Explanation:
    This class defines a loan schedule model with attributes month, remaining_balance, and monthly_payment.
    It represents the details of a loan schedule for a specific month.
    The attributes interest and principal are commented out, but could potentially be included in the model.

    Args:
        - month (int): The month of the loan schedule.
        - remaining_balance (float): The remaining balance of the loan for the given month.
        - monthly_payment (float): The monthly payment amount for the given month.

    Returns:
        - No return value for class methods.

    Raises:
        - No exceptions raised for class methods.

    Examples:
        - No examples provided for a class.
    """
    __pydantic_extra__: Dict[str, float]

    month: int
    remaining_balance: float
    monthly_payment: float
    # interest: float
    # principal: float

    # model_config = ConfigDict(extra='allow')


class LoanSummary(BaseModel):
    """
    Model representing a loan summary.

    Explanation:
    This class defines a loan summary model with attributes current_principal_balance, aggregate_principal_paid, and
        aggregate_interest_paid.
    It represents the summary of a loan, including the current principal balance, aggregate principal paid, and
        aggregate interest paid.

    Args:
        - current_principal_balance (float): The current principal balance of the loan.
        - aggregate_principal_paid (float): The aggregate amount of principal paid for the loan.
        - aggregate_interest_paid (float): The aggregate amount of interest paid for the loan.

    Returns:
        - No return value for class methods.

    Raises:
        - No exceptions raised for class methods.

    Examples:
        - No examples provided for a class.
    """

    current_principal_balance: float
    aggregate_principal_paid: float
    aggregate_interest_paid: float


class UserBase(BaseModel):
    """
    Base schema for a user.

    Explanation:
    This class serves as the base schema for a user, providing a foundation for defining user-related schemas.
    It includes an attribute email for representing the email address of a user.

    Args:
        - email (EmailStr): The email address of the user.

    Returns:
        - No return value for class methods.

    Raises:
        - No exceptions raised for class methods.

    Examples:
        - No examples provided for a class.
    """
    email: str


class UserCreate(UserBase):
    """
    Schema for creating a user.

    Explanation:
    This class defines a schema for creating a user, extending the UserBase schema.
    It includes an additional attribute password for representing the password of a user.

    Args:
        - password (SecretStr): The password of the user.

    Returns:
        - No return value for class methods.

    Raises:
        - No exceptions raised for class methods.

    Examples:
        - No examples provided for a class.
    """
    password: str


class User(UserBase):
    """
    Model representing a user.

    Explanation:
    This class defines a user model with attributes id, is_active, and loans.
    It extends the UserBase schema and includes a configuration class for attribute initialization.

    Args:
        - id (int): The ID of the user.
        - is_active (bool): Indicates whether the user is active or not.
        - loans (list[Loan]): A list of loans associated with the user.

    Returns:
        - No return value for class methods.

    Raises:
        - No exceptions raised for class methods.

    Examples:
        - No examples provided for a class.
    """
    id: int
    is_active: bool
    loans: list[Loan] = []

    class Config:
        from_attributes = True
