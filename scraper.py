from jobspy import scrape_jobs
import pandas as pd
import webbrowser
import os

def get_all_india_jobs():
    print(f"🚀 Searching across India for Full Stack vacancies...")
    
    # Scrape data
    jobs = scrape_jobs(
        site_name=["indeed", "linkedin", "google"],
        search_term="full stack developer",
        location="India",
        results_wanted=150, 
        country_indeed='india'
    )

    if not jobs.empty:
        # 1. Prepare Data
        df = jobs.fillna('N/A')
        
        # 2. Modern CSS Injection
        style = """
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #2563eb;
                --primary-hover: #1d4ed8;
                --bg: #f8fafc;
                --text-main: #1e293b;
                --text-muted: #64748b;
                --card-bg: #ffffff;
                --shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            }

            body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text-main); margin: 0; padding: 40px 20px; }
            .container { max-width: 1100px; margin: 0 auto; }
            
            header { text-align: center; margin-bottom: 40px; }
            header h1 { font-size: 2.5rem; font-weight: 800; margin-bottom: 10px; color: #0f172a; letter-spacing: -0.025em; }
            header p { color: var(--text-muted); font-size: 1.1rem; }

            /* Search/Filter Bar */
            .filter-container { margin-bottom: 30px; display: flex; justify-content: center; }
            #searchInput { 
                width: 100%; max-width: 500px; padding: 12px 20px; border-radius: 12px;
                border: 1px solid #e2e8f0; font-size: 1rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                outline: none; transition: border 0.2s;
            }
            #searchInput:focus { border-color: var(--primary); }

            /* Job Card Grid */
            .job-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 24px; }
            
            .job-card { 
                background: var(--card-bg); border-radius: 16px; padding: 24px;
                display: flex; flex-direction: column; justify-content: space-between;
                box-shadow: var(--shadow); border: 1px solid #f1f5f9;
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .job-card:hover { transform: translateY(-5px); box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1); }

            .site-tag { 
                display: inline-block; padding: 4px 10px; border-radius: 6px; 
                font-size: 0.75rem; font-weight: 700; text-transform: uppercase; 
                margin-bottom: 12px; background: #eff6ff; color: var(--primary);
            }
            
            .job-title { font-size: 1.25rem; font-weight: 700; margin: 0 0 8px 0; color: #0f172a; line-height: 1.4; }
            .company { font-weight: 500; color: #334155; margin-bottom: 4px; display: flex; align-items: center; gap: 6px; }
            .location { color: var(--text-muted); font-size: 0.9rem; margin-bottom: 16px; display: flex; align-items: center; gap: 6px; }
            
            .job-footer { margin-top: auto; padding-top: 16px; border-top: 1px solid #f1f5f9; display: flex; justify-content: space-between; align-items: center; }
            .date { font-size: 0.85rem; color: var(--text-muted); }
            
            .apply-btn { 
                background: var(--primary); color: white; padding: 10px 20px; 
                text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 0.9rem;
                transition: background 0.2s;
            }
            .apply-btn:hover { background: var(--primary-hover); }

            @media (max-width: 640px) { .job-grid { grid-template-columns: 1fr; } }
        </style>
        """

        # 3. Build Job Cards
        jobs_html = ""
        for _, job in df.iterrows():
            jobs_html += f"""
            <div class="job-card" data-title="{job['title'].lower()}" data-company="{job['company'].lower()}">
                <div>
                    <span class="site-tag">{job['site']}</span>
                    <h2 class="job-title">{job['title']}</h2>
                    <div class="company">🏢 {job['company']}</div>
                    <div class="location">📍 {job['location']}</div>
                </div>
                <div class="job-footer">
                    <span class="date">🕒 {job['date_posted']}</span>
                    <a href="{job['job_url']}" target="_blank" class="apply-btn">Apply Now</a>
                </div>
            </div>
            """

        # 4. Search Bar Logic (JavaScript)
        script = """
        <script>
            function filterJobs() {
                let input = document.getElementById('searchInput').value.toLowerCase();
                let cards = document.getElementsByClassName('job-card');
                for (let card of cards) {
                    let title = card.getAttribute('data-title');
                    let company = card.getAttribute('data-company');
                    if (title.includes(input) || company.includes(input)) {
                        card.style.display = "";
                    } else {
                        card.style.display = "none";
                    }
                }
            }
        </script>
        """

        # 5. Assemble and Save
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Full Stack India Dash</title>{style}</head>
        <body>
            <div class="container">
                <header>
                    <h1>🚀 India Tech Openings</h1>
                    <p>Found <b>{len(df)}</b> vacancies in the last search</p>
                </header>
                <div class="filter-container">
                    <input type="text" id="searchInput" onkeyup="filterJobs()" placeholder="Search by job title or company...">
                </div>
                <div class="job-grid">
                    {jobs_html}
                </div>
            </div>
            {script}
        </body>
        </html>
        """

        with open("full_india_vacancies.html", "w", encoding="utf-8") as f:
            f.write(full_html)
        
        webbrowser.open(os.path.abspath("full_india_vacancies.html"))
        print(f"✅ Creative Dashboard opened successfully!")
    else:
        print("❌ No jobs found.")

if __name__ == "__main__":
    get_all_india_jobs()