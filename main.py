import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Any, Dict

from database import db, create_document, get_documents
from schemas import Contact as ContactSchema, Schedule as ScheduleSchema

app = FastAPI(title="Content Craft Media API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello from FastAPI Backend!"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response: Dict[str, Any] = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = getattr(db, 'name', "✅ Connected")
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

# Inbound forms
@app.post("/contact")
def submit_contact(payload: ContactSchema):
    try:
        inserted_id = create_document("contact", payload)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/schedule")
def submit_schedule(payload: ScheduleSchema):
    try:
        inserted_id = create_document("schedule", payload)
        return {"status": "ok", "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Simple feed to remove blank spaces on frontend (projects, testimonials, pricing)
@app.get("/feed")
def feed():
    projects = [
        {
            "title": "D2C Beauty: 5.1x ROAS Launch",
            "image": "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?q=80&w=1600&auto=format&fit=crop",
            "tag": "E-commerce",
            "stats": {"roas": "5.1x", "spend": "₹12.4L", "revenue": "₹63.4L"}
        },
        {
            "title": "Fintech App: 120k Pre-Launch Signups",
            "image": "https://images.unsplash.com/photo-1556745753-b2904692b3cd?q=80&w=1600&auto=format&fit=crop",
            "tag": "Fintech",
            "stats": {"cpl": "₹42", "leads": "120k", "conv": "3.6%"}
        },
        {
            "title": "B2B SaaS: Pipeline +56% MoM",
            "image": "https://images.unsplash.com/photo-1556157382-97eda2d62296?q=80&w=1600&auto=format&fit=crop",
            "tag": "SaaS",
            "stats": {"mrr": "+56%", "acv": "+22%", "sql": "+41%"}
        }
    ]
    testimonials = [
        {"name": "Aarav Gupta", "role": "CMO, Nova Retail", "quote": "They rebuilt our growth engine. Results landed in week one."},
        {"name": "Maya Iyer", "role": "CEO, Helix Health", "quote": "Their brand + performance mix is rare. Creative that actually sells."},
        {"name": "Rohan Shah", "role": "Head of Growth, Quanta", "quote": "Clean ops, fast execution, and numbers to match."}
    ]
    pricing = [
        {"tier": "Starter", "price": "₹60k/mo", "features": ["Strategy sprint", "2 channels", "Monthly reporting"]},
        {"tier": "Growth", "price": "₹1.5L/mo", "features": ["Full-funnel", "4 channels", "Weekly sprints"]},
        {"tier": "Scale", "price": "Custom", "features": ["Dedicated squad", "Unlimited iterations", "Advanced analytics"]}
    ]
    return {"projects": projects, "testimonials": testimonials, "pricing": pricing}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
