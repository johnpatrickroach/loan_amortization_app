# Loan Amortization App

This is a REST API for a Loan Amortization app built using FastAPI.

## Setup

1. **Clone the Repository:**

    ```bash
    git clone https://github.com/johnpatrickroach/loan_amortization_app.git
    ```

2. **Install Dependencies:**

    Navigate to the project directory and install the required dependencies using pip:

    ```bash
    cd loan_amortization_app
    pip install -r requirements.txt
    ```

3. **Run the Application:**

    Start the FastAPI server using uvicorn:

    ```bash
    uvicorn main:app --reload
    ```

    The API will start running on `http://localhost:8000`. You can access the interactive API documentation (Swagger UI) at `http://localhost:8000/docs` and the alternative interactive API documentation (ReDoc) at `http://localhost:8000/redoc`.

## Endpoints

- `POST /users/`: Create a new user.
- `POST /users/{user_id}/loans/`: Create a loan for a specific user.
- `GET /users/{user_id}/loans/`: Get all loans for a user.
- `GET /loans/{loan_id}/schedule/`: Get the loan schedule for a loan.
- `GET /loans/{loan_id}/summary/{month}/`: Get the loan summary for a specific month.
- `POST /loans/{loan_id}/share/`: Share a loan with another user.

## Testing

To run tests, navigate to the `tests` directory and run pytest:

```bash
cd tests
pytest
```

## Authors

- [Patrick Roach](https://github.com/johnpatrickroach)