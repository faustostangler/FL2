import requests
import random
import time

from config import Config
import utils.logging as logging_utils
from utils.time_utils import sleep_dynamic

config = Config()

def header_random() -> dict:
    """Generate random HTTP headers for requests."""
    try:
        user_agent = random.choice(config.scraping.user_agents)
        referer = random.choice(config.scraping.referers)
        language = random.choice(config.scraping.languages)

        return {"User-Agent": user_agent, "Referer": referer, "Accept-Language": language}
    except Exception as e:
        logging_utils.log_message(e, level="debug")

        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
            "Referer": "https://www.google.com/",
            "Accept-Language": "en-US,en;q=0.9"
        }

def test_internet(url=None, timeout=None) -> bool:

    url = url or config.scraping.test_internet or "https://www.google.com"
    timeout = timeout or config.scraping.timeout or 5

    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except Exception as e:
        return False

def _fetch_with_retry(scraper, url, max_attempts=None, timeout=None):
    max_attempts = max_attempts or config.scraping.max_attempts or 5
    timeout = timeout or config.scraping.timeout or 5

    attempt = 0
    while attempt < max_attempts:
        try:
            response = scraper.get(url, headers=header_random())
            if response.status_code == 200:
                return response
        except Exception:
            pass
        attempt += 1
        # logging_utils.log_message(f"Attempt {attempt} failed for {url}", level="warning")
        sleep_dynamic(wait=timeout)
    raise ConnectionError(f"Failed to fetch {url} after {max_attempts} attempts.")
