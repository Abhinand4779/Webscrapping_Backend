import time
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class JobScraper:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # Run in background
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

    def get_driver(self):
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=self.chrome_options)
            return driver
        except Exception as e:
            print(f"Error initializing Chrome driver: {e}")
            return None

    def scrape_naukri(self, query, location):
        """
        Scrapes real jobs from Naukri.com using Selenium to bypass JS/Bot protection.
        """
        driver = self.get_driver()
        if not driver:
            return []

        # Format URL: https://www.naukri.com/python-jobs-in-kerala
        q = query.lower().replace(" ", "-")
        l = location.lower().replace(" ", "-")
        url = f"https://www.naukri.com/{q}-jobs-in-{l}"
        
        jobs = []
        try:
            driver.get(url)
            # Wait for job cards to appear
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "srp-jobtuple-wrapper"))
            )
            
            # Get page source and parse with BS4
            soup = BeautifulSoup(driver.page_source, "html.parser")
            job_cards = soup.select(".srp-jobtuple-wrapper")
            
            for card in job_cards[:10]:
                title_elem = card.select_one("a.title")
                company_elem = card.select_one("a.comp-name")
                loc_elem = card.select_one(".locWdth")
                sal_elem = card.select_one(".sal-wrap")
                link_elem = title_elem.get("href") if title_elem else url
                
                if title_elem:
                    jobs.append({
                        "title": title_elem.get_text(strip=True),
                        "company": company_elem.get_text(strip=True) if company_elem else "N/A",
                        "location": loc_elem.get_text(strip=True) if loc_elem else location,
                        "category": query,
                        "salary": sal_elem.get_text(strip=True) if sal_elem else "Not Disclosed",
                        "description": "Click link for details.",
                        "link": link_elem if link_elem.startswith("http") else f"https://www.naukri.com{link_elem}",
                        "source": "Naukri"
                    })
        except Exception as e:
            print(f"Naukri Scraping Error: {e}")
        finally:
            driver.quit()
        return jobs

    def get_all_jobs(self, query="Python", location="Kerala"):
        # Currently focusing on Naukri as it's the most reliable for real-world India jobs
        print(f"Scraping real jobs for '{query}' in '{location}'...")
        return self.scrape_naukri(query, location)

if __name__ == "__main__":
    scraper = JobScraper()
    jobs = scraper.get_all_jobs("Python", "Kerala")
    print(f"\n✅ Found {len(jobs)} real jobs:")
    for j in jobs:
        print(f"- {j['title']} | {j['company']} | {j['location']}")
