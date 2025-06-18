import requests
import random
import time

from config.config import Config

config = Config()

def header_random() -> dict:
    """Generate random HTTP headers for requests."""
    headers = {}
    try:
        user_agent = random.choice(config.scraping["user_agents"])
        referer = random.choice(config.scraping["referers"])
        language = random.choice(config.scraping["languages"])

        headers = {"User-Agent": user_agent, "Referer": referer, "Accept-Language": language}
    except Exception as e:
        print(e)

    return headers

def test_internet(url=None, timeout=None) -> bool:

    url = url or config.scraping["test_internet"] or "https://www.google.com"
    timeout = timeout or config.scraping["timeout"] or 5

    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except Exception as e:
        return False

def _fetch_with_retry(scraper, url, max_attempts=None, wait=None):
    max_attempts = max_attempts or config.scraping["max_attempts"] or 5
    wait = wait or config.global_settings["wait"] or 2

    attempt = 0
    while attempt < max_attempts:
        try:
            response = scraper.get(url, headers=header_random())
            if response.status_code == 200:
                return response
        except Exception:
            pass
        time.sleep(wait)
        attempt += 1
    raise ConnectionError(f"Failed to fetch {url} after {max_attempts} attempts.")
