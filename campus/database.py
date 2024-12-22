from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.declarative import declarative_base


hostname = "127.0.0.1"
port = "3306"
username = "root"
password = "raghu"
database = "campusdb"

DATABASE_URL = f"mysql+pymysql://{username}:{password}@{hostname}:{port}/{database}"

engine = create_engine(
    DATABASE_URL,
    connect_args={},
    poolclass=StaticPool
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
