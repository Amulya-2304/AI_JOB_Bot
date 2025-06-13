import os
import requests

def fetch_google_jobs(keyword, location):
    """Fetch job listings from Google Jobs via SerpAPI"""
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise ValueError("SERPAPI_KEY not found in environment.")

    url = "https://serpapi.com/search"
    params = {
        "engine": "google_jobs",
        "q": keyword,
        "location": location,
        "api_key": api_key
    }

    response = requests.get(url, params=params)
    data = response.json()

    results = []
    for job in data.get("jobs_results", []):
        results.append({
            "title": job.get("title"),
            "company": job.get("company_name"),
            "location": job.get("location"),
            "via": "Google Jobs",
            "description": job.get("description"),
            "link": job.get("related_links", [{}])[0].get("link")
        })

    return results