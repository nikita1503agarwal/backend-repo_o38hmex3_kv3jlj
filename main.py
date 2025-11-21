import os
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Job, Application

app = FastAPI(title="CyberSec Jobs API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Cybersecurity Recruitment API running"}

@app.get("/schema")
def get_schema_info():
    # Expose schema names for admin viewers
    return {"collections": ["job", "application"]}

# Jobs endpoints
@app.post("/jobs")
def create_job(job: Job):
    try:
        job_id = create_document("job", job)
        return {"id": job_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs")
def list_jobs(country: Optional[str] = None, q: Optional[str] = None, limit: int = 50):
    try:
        filter_dict = {}
        if country:
            filter_dict["country"] = country
        docs = get_documents("job", filter_dict, limit)
        # simple search in title/company if q provided
        results = []
        for d in docs:
            d["id"] = str(d.get("_id"))
            d.pop("_id", None)
            if q:
                hay = (d.get("title", "") + " " + d.get("company", "") + " " + d.get("description", "")).lower()
                if q.lower() in hay:
                    results.append(d)
            else:
                results.append(d)
        return {"items": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    try:
        doc = db["job"].find_one({"_id": ObjectId(job_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Job not found")
        doc["id"] = str(doc["_id"]) 
        doc.pop("_id", None)
        return doc
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Applications endpoints
@app.post("/applications")
async def submit_application(
    job_id: str = Form(...),
    name: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    linkedin: Optional[str] = Form(None),
    cover_letter: Optional[str] = Form(None),
    cv: UploadFile = File(...)
):
    try:
        # For demo: store the CV in a temp folder and return a local URL
        uploads_dir = os.path.join("uploads")
        os.makedirs(uploads_dir, exist_ok=True)
        filename = f"{ObjectId()}_{cv.filename}"
        file_path = os.path.join(uploads_dir, filename)
        with open(file_path, "wb") as f:
            f.write(await cv.read())
        cv_url = f"/files/{filename}"

        app_doc = Application(
            job_id=job_id,
            name=name,
            email=email,
            phone=phone,
            linkedin=linkedin,
            cover_letter=cover_letter,
            cv_url=cv_url,
        )
        app_id = create_document("application", app_doc)
        return {"id": app_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/applications", response_class=JSONResponse)
def list_applications(limit: int = 50):
    try:
        docs = get_documents("application", {}, limit)
        for d in docs:
            d["id"] = str(d.get("_id"))
            d.pop("_id", None)
        return {"items": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Static file serving for uploaded CVs
from fastapi.staticfiles import StaticFiles
app.mount("/files", StaticFiles(directory="uploads", check_dir=False), name="files")

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
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
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

    import os as _os
    response["database_url"] = "✅ Set" if _os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if _os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
