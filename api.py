from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from jobspy import scrape_jobs
import pandas as pd
from typing import Optional

app = FastAPI(title="India Job Finder API")

# Enable CORS so your browser can talk to the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/jobs")
async def get_jobs(
    role: str = Query("full stack developer", description="Job title"),
    location: str = Query("India", description="Location"),
    limit: int = Query(50, description="Number of results")
):
    print(f"📡 API request received: {role} in {location}")
    try:
        # Re-using your exact logic
        jobs = scrape_jobs(
            site_name=["indeed", "linkedin", "google"],
            search_term=role,
            location=location,
            results_wanted=limit,
            country_indeed='india'
        )

        if jobs.empty:
            return {"status": "success", "count": 0, "jobs": []}

        # Clean data for JSON (removes NaNs which break JSON)
        jobs = jobs.fillna('N/A')
        
        # Convert to a list of dictionaries
        job_list = jobs.to_dict(orient='records')

        return {
            "status": "success",
            "count": len(job_list),
            "metadata": {"role": role, "location": location},
            "jobs": job_list
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    # Running on port 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)