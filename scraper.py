import time
import random
import os
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
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")

        # Automatically use Chrome installed in Render's environment if it exists
        render_chrome_path = "/opt/render/project/.render/chrome/opt/google/chrome/google-chrome"
        if os.path.exists(render_chrome_path):
            self.chrome_options.binary_location = render_chrome_path

    def get_driver(self):
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=self.chrome_options)
            return driver
        except Exception as e:
            print(f"Error initializing Chrome driver: {e}")
            return None

    def scrape_naukri(self, query, location):
        driver = self.get_driver()
        if not driver: return []
        q = query.lower().replace(" ", "-")
        l = location.lower().replace(" ", "-")
        url = f"https://www.naukri.com/{q}-jobs-in-{l}"
        jobs = []
        try:
            driver.get(url)
            # Wait for any of the common card selectors
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".srp-jobtuple-wrapper, .jobTuple"))
            )
            soup = BeautifulSoup(driver.page_source, "html.parser")
            job_cards = soup.select(".srp-jobtuple-wrapper, .jobTuple")
            for card in job_cards[:5]:
                title_elem = card.select_one("a.title")
                company_elem = card.select_one("a.comp-name")
                loc_elem = card.select_one(".locWdth")
                sal_elem = card.select_one(".sal-wrap")
                if title_elem:
                    link = title_elem.get("href", "")
                    jobs.append({
                        "title": title_elem.get_text(strip=True),
                        "company": company_elem.get_text(strip=True) if company_elem else "N/A",
                        "location": loc_elem.get_text(strip=True) if loc_elem else location,
                        "salary": sal_elem.get_text(strip=True) if sal_elem else "Not Disclosed",
                        "link": link if link.startswith("http") else f"https://www.naukri.com{link}",
                        "source": "Naukri",
                        "description": "View details on Naukri."
                    })
        except Exception as e: print(f"Naukri Error: {e}")
        finally: driver.quit()
        return jobs

    def scrape_linkedin(self, query, location):
        driver = self.get_driver()
        if not driver: return []
        url = f"https://www.linkedin.com/jobs/search?keywords={query}&location={location}"
        jobs = []
        try:
            driver.get(url)
            time.sleep(4)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            job_cards = soup.select(".base-search-card")
            for card in job_cards[:5]:
                title_elem = card.select_one(".base-search-card__title")
                company_elem = card.select_one(".base-search-card__subtitle")
                loc_elem = card.select_one(".job-search-card__location")
                link_elem = card.select_one(".base-card__full-link")
                if title_elem:
                    jobs.append({
                        "title": title_elem.get_text(strip=True),
                        "company": company_elem.get_text(strip=True) if company_elem else "N/A",
                        "location": loc_elem.get_text(strip=True) if loc_elem else location,
                        "salary": "Not Disclosed",
                        "link": link_elem.get("href", "") if link_elem else url,
                        "source": "LinkedIn",
                        "description": "View details on LinkedIn."
                    })
        except Exception as e: print(f"LinkedIn Error: {e}")
        finally: driver.quit()
        return jobs

    def scrape_internshala(self, query, location):
        driver = self.get_driver()
        if not driver: return []
        url = f"https://internshala.com/jobs/keywords-{query.replace(' ', '%20')}"
        jobs = []
        try:
            driver.get(url)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            job_cards = soup.select(".individual_internship")
            for card in job_cards[:5]:
                title_elem = card.select_one(".job-title-container a") or card.select_one(".profile a")
                company_elem = card.select_one(".company_name")
                loc_elem = card.select_one(".location_link")
                sal_elem = card.select_one(".stipend")
                if title_elem:
                    link = title_elem.get("href", "")
                    jobs.append({
                        "title": title_elem.get_text(strip=True),
                        "company": company_elem.get_text(strip=True) if company_elem else "N/A",
                        "location": loc_elem.get_text(strip=True) if loc_elem else location,
                        "salary": sal_elem.get_text(strip=True) if sal_elem else "Not Disclosed",
                        "link": f"https://internshala.com{link}" if link.startswith("/") else link,
                        "source": "Internshala",
                        "description": "View details on Internshala."
                    })
        except Exception as e: print(f"Internshala Error: {e}")
        finally: driver.quit()
        return jobs

    def scrape_indeed(self, query, location):
        driver = self.get_driver()
        if not driver: return []
        url = f"https://in.indeed.com/jobs?q={query}&l={location}"
        jobs = []
        try:
            driver.get(url)
            time.sleep(4)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            job_cards = soup.select(".job_seen_beacon")
            for card in job_cards[:5]:
                title_elem = card.select_one("h2.jobTitle span")
                company_elem = card.select_one("[data-testid='company-name']")
                loc_elem = card.select_one("[data-testid='text-location']")
                sal_elem = card.select_one(".salary-snippet-container")
                link_elem = card.select_one("h2.jobTitle a")
                if title_elem:
                    link = link_elem.get("href", "") if link_elem else ""
                    jobs.append({
                        "title": title_elem.get_text(strip=True),
                        "company": company_elem.get_text(strip=True) if company_elem else "N/A",
                        "location": loc_elem.get_text(strip=True) if loc_elem else location,
                        "salary": sal_elem.get_text(strip=True) if sal_elem else "Not Disclosed",
                        "link": f"https://in.indeed.com{link}" if link.startswith("/") else link,
                        "source": "Indeed",
                        "description": "View details on Indeed."
                    })
        except Exception as e: print(f"Indeed Error: {e}")
        finally: driver.quit()
        return jobs

    def scrape_glassdoor(self, query, location):
        driver = self.get_driver()
        if not driver: return []
        url = f"https://www.glassdoor.com/Job/jobs.htm?sc.keyword={query}&locK={location}"
        jobs = []
        try:
            driver.get(url)
            time.sleep(4)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            job_cards = soup.select(".react-job-listing, .job-listing")
            for card in job_cards[:5]:
                title_elem = card.select_one(".job-title, [data-test='job-title']")
                company_elem = card.select_one(".employer-name, [data-test='employer-name']")
                loc_elem = card.select_one(".location, [data-test='location']")
                sal_elem = card.select_one(".salary-estimate, [data-test='detailSalary']")
                link_elem = card.select_one("a.job-link") or card.find("a", href=True)
                if title_elem:
                    link = link_elem.get("href", "") if link_elem else ""
                    jobs.append({
                        "title": title_elem.get_text(strip=True),
                        "company": company_elem.get_text(strip=True) if company_elem else "N/A",
                        "location": loc_elem.get_text(strip=True) if loc_elem else location,
                        "salary": sal_elem.get_text(strip=True) if sal_elem else "Not Disclosed",
                        "link": link if link.startswith("http") else f"https://www.glassdoor.com{link}",
                        "source": "Glassdoor",
                        "description": "View details on Glassdoor."
                    })
        except Exception as e: print(f"Glassdoor Error: {e}")
        finally: driver.quit()
        return jobs

    def get_all_jobs(self, query="Python", location="Kerala"):
        all_results = []
        print(f"Scraping results for '{query}' in '{location}'...")
        
        # Call each platform
        platforms = [
            ("Naukri", self.scrape_naukri),
            ("LinkedIn", self.scrape_linkedin),
            ("Internshala", self.scrape_internshala),
            ("Indeed", self.scrape_indeed),
            ("Glassdoor", self.scrape_glassdoor)
        ]
        
        for name, scrape_func in platforms:
            try:
                print(f"Searching {name}...")
                results = scrape_func(query, location)
                all_results.extend(results)
                print(f"Found {len(results)} jobs on {name}")
            except Exception as e:
                print(f"Error in {name} scraper: {e}")
                
        return all_results

if __name__ == "__main__":
    scraper = JobScraper()
    jobs = scraper.get_all_jobs("Python", "Kerala")
    print(f"\nTotal jobs found: {len(jobs)}")
    for j in jobs:
        print(f"[{j['source']}] {j['title']} - {j['company']}")
