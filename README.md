# 🕸️ Real-Time Job Scraper

A lightweight Python API built with FastAPI that scrapes job listings from popular portals in real-time. No database or authentication required.

## 🚀 Features

- **Multi-Platform Scraping**: Fetches real-world data from **Naukri, LinkedIn, Indeed, Glassdoor**, and **Internshala**.
- **No Database**: Completely independent, no setup required.
- **Selenium Powered**: Uses headless browser technology to bypass modern bot protections.

## 🛠️ Tech Stack

- **Python 3.x**
- **FastAPI** (Web Framework)
- **BeautifulSoup4** (HTML Parsing)
- **Requests** (HTTP Client)

## 📌 Getting Started

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the server**:
   ```bash
   python main.py
   ```

3. **Scrape Jobs**:
   - Open your browser to: `http://localhost:8000/jobs?query=python&location=kerala`
   - View the interactive docs: `http://localhost:8000/docs`

## 📂 Project Structure

- `main.py`: FastAPI routes and application logic.
- `scraper.py`: Core scraping logic using BeautifulSoup.
- `requirements.txt`: Python package dependencies.
