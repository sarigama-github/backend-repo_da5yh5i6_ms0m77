import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Trainer, Testimonial, ContractRequest, Service

app = FastAPI(title="Edufuser API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Edufuser backend is running"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response


# Seed default services and sample trainers/testimonials if empty to make frontend work immediately
DEFAULT_SERVICES: List[Service] = [
    Service(title="Short-Term Course Teaching", icon="BookOpen", description="Intensive short-term courses tailored to your curriculum."),
    Service(title="Workshops & Seminars", icon="Presentation", description="Interactive, hands-on workshops and knowledge-sharing seminars."),
    Service(title="Motivational Speaking", icon="Mic", description="High-energy sessions to inspire and motivate audiences."),
    Service(title="Corporate/Professional Training", icon="Briefcase", description="Skill-building programs for teams and organizations."),
    Service(title="Customized Programs", icon="Settings", description="Training designed around your unique goals and audience."),
]

SAMPLE_TRAINERS: List[Trainer] = [
    Trainer(
        name="Aisha Khan",
        photo_url="https://images.unsplash.com/photo-1544005313-94ddf0286df2?q=80&w=600&auto=format&fit=crop",
        bio="Leadership coach and corporate trainer with 10+ years of experience.",
        expertise=["Leadership", "Communication", "Team Building"],
        certifications=["ICF Certified", "PMP"],
        rating=4.8,
    ),
    Trainer(
        name="Daniel Park",
        photo_url="https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?q=80&w=600&auto=format&fit=crop",
        bio="Technology educator specializing in workshops and bootcamps.",
        expertise=["Python", "Data Analysis", "AI Literacy"],
        certifications=["AWS CP", "Azure AI-900"],
        rating=4.7,
    ),
]

SAMPLE_TESTIMONIALS: List[Testimonial] = [
    Testimonial(author="Greenfield University", role="Dept. of CS", quote="Edufuser delivered exactly what our faculty needed.", rating=5),
    Testimonial(author="Nexus Corp.", role="HR Director", quote="The motivational program energized our teams.", rating=5),
]


@app.get("/api/services", response_model=List[Service])
def list_services():
    try:
        # Try from DB if collection exists
        if db and "service" in db.list_collection_names():
            docs = get_documents("service")
            # Ensure keys align with Pydantic model
            services = [Service(**{k: v for k, v in d.items() if k in Service.model_fields}) for d in docs]
            if services:
                return services
    except Exception:
        pass
    # Fallback to defaults
    return DEFAULT_SERVICES


@app.get("/api/trainers", response_model=List[Trainer])
def list_trainers():
    try:
        if db and "trainer" in db.list_collection_names():
            docs = get_documents("trainer")
            trainers = []
            for d in docs:
                data = {k: v for k, v in d.items() if k in Trainer.model_fields}
                trainers.append(Trainer(**data))
            if trainers:
                return trainers
    except Exception:
        pass
    return SAMPLE_TRAINERS


@app.get("/api/testimonials", response_model=List[Testimonial])
def list_testimonials():
    try:
        if db and "testimonial" in db.list_collection_names():
            docs = get_documents("testimonial")
            t = [Testimonial(**{k: v for k, v in d.items() if k in Testimonial.model_fields}) for d in docs]
            if t:
                return t
    except Exception:
        pass
    return SAMPLE_TESTIMONIALS


@app.post("/api/contract-request")
def submit_contract_request(payload: ContractRequest):
    try:
        if db:
            inserted_id = create_document("contractrequest", payload)
            return {"status": "ok", "id": inserted_id}
        else:
            # Accept but mark as not persisted
            return {"status": "ok", "id": None, "note": "Database not configured; data not persisted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
