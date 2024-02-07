from fastapi import HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from api.database import Base
from api.main import app, get_db

TEST_SQLALCHEMY_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base.metadata.create_all(bind=test_engine)


def override_get_db() -> Session:
    db = None
    try:
        db: Session | None = TestingSessionLocal()
        yield db
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error") from e
    finally:
        if db:
            db.close()


# noinspection PyUnresolvedReferences
app.dependency_overrides[get_db] = override_get_db

test_client = TestClient(app)


def test_index():
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}


def test_get_users_endpoint():
    response = test_client.get("/users/")
    assert response.status_code == 200
    assert response.json() == []


def test_create_user_endpoint():
    response = test_client.post(
        "/users/",
        json={"email": "test@example.com", "password": "test"},
    )
    assert response.status_code == 200


def test_create_user_endpoint_email_exists():
    response = test_client.post(
        "/users/",
        json={"email": "test2@example.com", "password": "test2"},
    )
    assert response.status_code == 200

    response2 = test_client.post(
        "/users/",
        json={"email": "test2@example.com", "password": "test2"},
    )
    assert response2.status_code == 400
    assert response2.text == '{"detail":"Email test2@example.com already registered"}'


def test_create_loan_for_user_endpoint():
    response = test_client.post(
        "/users/",
        json={"email": "test3@example.com", "password": "test3"},
    )
    assert response.status_code == 200

    user_id = response.json()["id"]

    response = test_client.post(
        f"/users/{user_id}/loans/",
        json={
            "amount": 1000.0,
            "annual_interest_rate": 5.0,
            "loan_term_months": 36,
            "frequency": 12,
        }
    )

    assert response.status_code == 200
    assert response.json() == {"id": 1, "user_id": user_id}


def test_get_user_loans_endpoint():
    response = test_client.post(
        "/users/",
        json={"email": "test4@example.com", "password": "test4"},
    )
    assert response.status_code == 200

    user_id = response.json()["id"]

    response = test_client.post(
        f"/users/{user_id}/loans/",
        json={
            "amount": 1000.0,
            "annual_interest_rate": 5.0,
            "loan_term_months": 36,
            "frequency": 12,
        }
    )

    assert response.status_code == 200

    loan_id = response.json()["id"]

    response = test_client.get(f"/users/{user_id}/loans/")
    assert response.status_code == 200
    assert response.json() == [{"id": loan_id, "user_id": user_id}]


def test_get_loan_schedule_endpoint():
    response = test_client.post(
        "/users/",
        json={"email": "test5@example.com", "password": "test5"},
    )
    assert response.status_code == 200

    user_id = response.json()["id"]

    response = test_client.post(
        f"/users/{user_id}/loans/",
        json={
            "amount": 1000.0,
            "annual_interest_rate": 5.0,
            "loan_term_months": 36,
            "frequency": 12,
        }
    )

    assert response.status_code == 200

    loan_id = response.json()["id"]

    response = test_client.get(f"/loans/{loan_id}/schedule/")
    assert response.status_code == 200
    assert response.json() == [{"month": 1, "remaining_balance": 974.2, "monthly_payment": 29.97},
                               {"month": 2, "remaining_balance": 948.29, "monthly_payment": 29.97},
                               {"month": 3, "remaining_balance": 922.27, "monthly_payment": 29.97},
                               {"month": 4, "remaining_balance": 896.14, "monthly_payment": 29.97},
                               {"month": 5, "remaining_balance": 869.9, "monthly_payment": 29.97},
                               {"month": 6, "remaining_balance": 843.55, "monthly_payment": 29.97},
                               {"month": 7, "remaining_balance": 817.09, "monthly_payment": 29.97},
                               {"month": 8, "remaining_balance": 790.52, "monthly_payment": 29.97},
                               {"month": 9, "remaining_balance": 763.84, "monthly_payment": 29.97},
                               {"month": 10, "remaining_balance": 737.05, "monthly_payment": 29.97},
                               {"month": 11, "remaining_balance": 710.15, "monthly_payment": 29.97},
                               {"month": 12, "remaining_balance": 683.14, "monthly_payment": 29.97},
                               {"month": 13, "remaining_balance": 656.02, "monthly_payment": 29.97},
                               {"month": 14, "remaining_balance": 628.78, "monthly_payment": 29.97},
                               {"month": 15, "remaining_balance": 601.43, "monthly_payment": 29.97},
                               {"month": 16, "remaining_balance": 573.97, "monthly_payment": 29.97},
                               {"month": 17, "remaining_balance": 546.39, "monthly_payment": 29.97},
                               {"month": 18, "remaining_balance": 518.7, "monthly_payment": 29.97},
                               {"month": 19, "remaining_balance": 490.89, "monthly_payment": 29.97},
                               {"month": 20, "remaining_balance": 462.97, "monthly_payment": 29.97},
                               {"month": 21, "remaining_balance": 434.93, "monthly_payment": 29.97},
                               {"month": 22, "remaining_balance": 406.77, "monthly_payment": 29.97},
                               {"month": 23, "remaining_balance": 378.49, "monthly_payment": 29.97},
                               {"month": 24, "remaining_balance": 350.1, "monthly_payment": 29.97},
                               {"month": 25, "remaining_balance": 321.59, "monthly_payment": 29.97},
                               {"month": 26, "remaining_balance": 292.96, "monthly_payment": 29.97},
                               {"month": 27, "remaining_balance": 264.21, "monthly_payment": 29.97},
                               {"month": 28, "remaining_balance": 235.34, "monthly_payment": 29.97},
                               {"month": 29, "remaining_balance": 206.35, "monthly_payment": 29.97},
                               {"month": 30, "remaining_balance": 177.24, "monthly_payment": 29.97},
                               {"month": 31, "remaining_balance": 148.01, "monthly_payment": 29.97},
                               {"month": 32, "remaining_balance": 118.66, "monthly_payment": 29.97},
                               {"month": 33, "remaining_balance": 89.18, "monthly_payment": 29.97},
                               {"month": 34, "remaining_balance": 59.58, "monthly_payment": 29.97},
                               {"month": 35, "remaining_balance": 29.86, "monthly_payment": 29.97},
                               {"month": 36, "remaining_balance": 0.0, "monthly_payment": 29.98}]


def test_get_loan_summary_endpoint():
    response = test_client.post(
        "/users/",
        json={"email": "test6@example.com", "password": "test6"},
    )
    assert response.status_code == 200

    user_id = response.json()["id"]

    response = test_client.post(
        f"/users/{user_id}/loans/",
        json={
            "amount": 1000.0,
            "annual_interest_rate": 5.0,
            "loan_term_months": 36,
            "frequency": 12,
        }
    )

    assert response.status_code == 200

    loan_id = response.json()["id"]

    response = test_client.get(f"/loans/{loan_id}/summary/14/")
    assert response.status_code == 200
    assert response.json() == {"current_principal_balance": 628.78, "aggregate_principal_paid": 371.22,
                               "aggregate_interest_paid": 48.36}


def test_share_loan_endpoint():
    response = test_client.post(
        "/users/",
        json={"email": "test7@example.com", "password": "test7"},
    )
    assert response.status_code == 200

    user_id1 = response.json()["id"]

    response = test_client.post(
        f"/users/{user_id1}/loans/",
        json={
            "amount": 1000.0,
            "annual_interest_rate": 5.0,
            "loan_term_months": 36,
            "frequency": 12,
        }
    )

    assert response.status_code == 200

    loan_id = response.json()["id"]

    response = test_client.post(
        "/users/",
        json={"email": "test8@example.com", "password": "test8"},
    )
    assert response.status_code == 200

    user_id2 = response.json()["id"]

    response = test_client.post(
        f"/loans/{loan_id}/share/?user_id={user_id2}",
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Loan shared successfully"}
