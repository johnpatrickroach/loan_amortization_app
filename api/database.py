from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL: str = "sqlite:///loan_amortization_app.db"  # In-memory SQLite database
engine = create_engine(
   SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Define Base class for SQLAlchemy models
Base = declarative_base()
