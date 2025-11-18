from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import os
from dotenv import load_dotenv
from database import db

load_dotenv()

app = FastAPI(title="Content Craft Media API", version="1.0.0")

# CORS for frontend
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ContactMessage(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    company: Optional[str] = None
    phone: Optional[str] = Field(None, max_length=20)
    message: str = Field(..., min_length=10, max_length=2000)
    service_interest: Optional[str] = Field(None, description="What service are they interested in")

class ScheduleCall(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    preferred_date: Optional[str] = None
    preferred_time: Optional[str] = None
    notes: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Content Craft Media API is running"}

@app.get("/test")
async def test_connection():
    # Provide DB connection details
    db_status = "connected" if db is not None else "not configured"
    collections = []
    if db is not None:
        try:
            collections = db.list_collection_names()
        except Exception:
            collections = []
    return {
        "backend": "FastAPI",
        "database": "MongoDB",
        "database_url": "configured" if os.getenv("DATABASE_URL") else "missing",
        "database_name": os.getenv("DATABASE_NAME", "missing"),
        "connection_status": db_status,
        "collections": collections,
    }

@app.post("/contact")
async def submit_contact(payload: ContactMessage):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    doc = payload.model_dump()
    try:
        res = db["contactmessage"].insert_one({**doc})
        return {"status": "ok", "id": str(res.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/schedule")
async def schedule_call(payload: ScheduleCall):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not available")
    doc = payload.model_dump()
    try:
        res = db["schedulecall"].insert_one({**doc})
        return {"status": "ok", "id": str(res.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

