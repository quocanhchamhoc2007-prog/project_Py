from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine

DATABASE_URL = "mysql+pymysql://root:%40Phamquocanh15072007@127.0.0.1:3306/club_db"

engine = create_engine(DATABASE_URL)

Base = declarative_base()

Localsesson = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False
)

def get_db():
    db = Localsesson()
    try:
        yield db
    finally:
        db.close()