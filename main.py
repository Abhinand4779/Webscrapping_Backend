from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from scraper import JobScraper

# --- MODELS ---
class JobSchema(BaseModel):
    title: str
    company: str
    location: str
    category: Optional[str] = None
    salary: Optional[str] = "Not Disclosed"
    description: Optional[str] = ""
    link: str
    source: str

# Initialize FastAPI app
app = FastAPI(
    title="Real-Time Job Scraper",
    description="API for scraping jobs from various portals without Auth/DB",
    version="2.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Scraper
scraper = JobScraper()

# --- ENDPOINTS ---

@app.get("/", tags=["Root"])
async def read_root():
    """Root endpoint"""
    return {
        "message": "Welcome to the Real-Time Job Scraper API",
        "version": "2.0.0",
        "status": "Running (No Auth/DB Required)",
        "usage": "Go to /jobs?query=python&location=kerala to scrape jobs"
    }

@app.get("/jobs", response_model=List[JobSchema], tags=["Jobs"])
async def get_jobs(
    query: str = Query("Python", description="Job title or keywords"),
    location: str = Query("Kerala", description="Location to search in")
):
    """
    Fetch jobs in real-time using the scraper (No DB/Auth)
    """
    try:
        jobs = scraper.get_all_jobs(query=query, location=location)
        return jobs
    except Exception as e:
        return {"error": f"Scraping failed: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=(os.getenv("PORT") is None))
