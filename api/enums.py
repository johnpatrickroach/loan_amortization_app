from enum import IntEnum


class PaymentFrequency(IntEnum):
    """
    Enumeration representing different payment frequencies.

    Explanation:
    This class defines an enumeration of payment frequencies, such as daily, biweekly, weekly, etc.
    Each payment frequency is associated with a corresponding integer value.

    Args:
        - No arguments required for class methods.

    Attributes:
        - No attributes for this class.

    Returns:
        - No return value for class methods.

    Raises:
        - No exceptions raised for class methods.

    Examples:
        - No examples provided for a class.
    """

    DAILY = 365
    BIWEEKLY = 104
    WEEKLY = 52
    SEMIMONTHLY = 24
    MONTHLY = 12
    QUARTERLY = 4
    SEMIYEARLY = 2
    YEARLY = 1
