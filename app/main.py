from fastapi import FastAPI

from app.db.database import Base, engine
from app.models.user import User
from app.models.club import Club, ClubMember
from app.models.activity import ClubActivity

from app.routers import auth, users, club

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {
        "success": True,
        "message": "Welcome to Club Management API"
    }


@app.get("/health")
def health_check():
    return {
        "success": True,
        "message": "Club Management API is running",
        "data": {
            "status": "healthy"
        }
    }


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(club.router)