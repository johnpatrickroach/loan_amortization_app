import factory
from api.models import User
from api.schemas import LoanCreate


class UserFactory(factory.Factory):
    class Meta:
        model = User

    email = factory.Faker("email")
    hashed_password = factory.Faker("password")


class LoanCreateFactory(factory.Factory):
    class Meta:
        model = LoanCreate

    amount = factory.Faker("pyint")
    annual_interest_rate = factory.Faker("pyfloat")
    loan_term_months = factory.Faker("pyint")
    frequency = factory.Faker("random_element", elements=[52, 24, 12])
