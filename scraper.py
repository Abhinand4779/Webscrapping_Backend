import pandas as pd
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import HTMLResponse
from jobspy import scrape_jobs
import uvicorn
import logging

# Set up logging to see what's happening without crashing
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Kerala Tech Job Portal API")

# Memory store for jobs
job_store = {
    "df": pd.DataFrame(),
    "html": "<html><body><h1>Initial scrape in progress...</h1><p>Please refresh in 60 seconds.</p></body></html>",
    "is_running": False
}

CATEGORIES = {
    "Digital Marketing": "Digital Marketing OR SEO OR Social Media",
    "MERN Stack": "MERN Stack OR React Node OR MongoDB",
    "UI/UX": "UI/UX Designer OR Product Designer",
    "Python": "Python Developer OR Django OR Flask"
}

def generate_html_dashboard(df):
    """Generates the modern UI layout"""
    if df.empty:
        return "<html><body><h1>No jobs found.</h1><p>Try triggering a /scrape.</p></body></html>"
    
    style = """
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
    <style>
        :root { --primary: #059669; --bg: #f0fdf4; --text: #111827; }
        body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }
        .header { background: white; padding: 40px; border-radius: 20px; text-align: center; margin-bottom: 30px; border: 1px solid #d1fae5; }
        .search-container { position: sticky; top: 10px; z-index: 100; margin-bottom: 30px; text-align: center; }
        #searchInput { width: 80%; max-width: 600px; padding: 15px 25px; border-radius: 50px; border: 2px solid #059669; font-size: 1rem; outline: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 20px; }
        .card { background: white; border-radius: 12px; padding: 20px; transition: 0.3s; border-left: 6px solid #059669; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .card:hover { transform: translateY(-5px); box-shadow: 0 10px 15px rgba(0,0,0,0.1); }
        .cat-badge { font-size: 0.7rem; font-weight: bold; padding: 4px 10px; border-radius: 4px; background: #ecfdf5; color: #065f46; display: inline-block; margin-bottom: 10px; border: 1px solid #059669; }
        .site-label { float: right; font-size: 0.65rem; color: #6b7280; text-transform: uppercase; font-weight: 800; }
        .title { font-size: 1.15rem; font-weight: 700; margin-bottom: 5px; color: #111827; }
        .company { color: #374151; font-weight: 600; font-size: 0.95rem; }
        .meta { font-size: 0.85rem; color: #6b7280; margin: 10px 0; }
        .btn { display: block; background: #059669; color: white; text-align: center; padding: 10px; border-radius: 8px; text-decoration: none; font-weight: 600; margin-top: 15px; }
    </style>
    """
    
    cards_html = ""
    for _, job in df.iterrows():
        search_data = f"{job['title']} {job['company']} {job['location']} {job['category_tag']}".lower()
        cards_html += f"""
        <div class="card" data-search="{search_data}">
            <span class="site-label">{job['site']}</span>
            <span class="cat-badge">{job['category_tag']}</span>
            <div class="title">{job['title']}</div>
            <div class="company">🏢 {job['company']}</div>
            <div class="meta">📍 {job['location']} | 🕒 {job['date_posted']}</div>
            <a href="{job['job_url']}" target="_blank" class="btn">Apply Now</a>
        </div>
        """

    js = """
    <script>
        function filter() {
            let q = document.getElementById('searchInput').value.toLowerCase();
            document.querySelectorAll('.card').forEach(c => {
                c.style.display = c.getAttribute('data-search').includes(q) ? "" : "none";
            });
        }
    </script>
    """
    return f"<html><head>{style}</head><body>" \
           f"<div class='header'><h1>🌴 Kerala Tech Jobs</h1><p>Found <b>{len(df)}</b> active vacancies</p></div>" \
           f"<div class='search-container'><input type='text' id='searchInput' onkeyup='filter()' placeholder='Search Kochi, MERN, etc...'></div>" \
           f"<div class='grid'>{cards_html}</div>{js}</body></html>"

def run_scraper():
    """Background task to fetch jobs"""
    if job_store["is_running"]:
        return
    
    job_store["is_running"] = True
    all_jobs_list = []
    
    for category_name, query in CATEGORIES.items():
        logger.info(f"🔍 Scraping {category_name}...")
        try:
            # Removed Glassdoor from site_name to avoid the 400 Bad Request error
            jobs = scrape_jobs(
                site_name=["linkedin", "indeed", "google"],
                search_term=query,
                location="Kerala, India",
                results_wanted=3000,
                country_indeed='india',
                hours_old=504,
                verbose=0
            )
            if not jobs.empty:
                jobs['category_tag'] = category_name
                all_jobs_list.append(jobs)
        except Exception as e:
            logger.error(f"❌ Error on {category_name}: {e}")

    if all_jobs_list:
        df = pd.concat(all_jobs_list).fillna('N/A').drop_duplicates(subset=['title', 'company'])
        job_store["df"] = df
        job_store["html"] = generate_html_dashboard(df)
        logger.info("✅ Scrape complete. Dashboard updated.")
    
    job_store["is_running"] = False

@app.on_event("startup")
async def startup_event():
    """Triggers the first scrape when the app starts"""
    # Start the scraper in a background thread so it doesn't block startup
    import threading
    threading.Thread(target=run_scraper).start()

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    return job_store["html"]

@app.get("/jobs")
async def get_json():
    if job_store["df"].empty:
        return {"status": "loading", "message": "Scraper is still running for the first time."}
    return job_store["df"].to_dict(orient="records")

@app.get("/scrape")
async def manual_scrape(background_tasks: BackgroundTasks):
    background_tasks.add_task(run_scraper)
    return {"message": "Scrape started in background."}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)