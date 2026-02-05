import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from urllib.parse import urljoin


class WebParser:
    """
    Universal web scraper supporting:
    - Static pages (requests + BeautifulSoup)
    - Dynamic pages (Selenium)
    - Clean text extraction
    - Hyperlink extraction for RAG grounding
    """

    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        }

    # =========================
    # Shared helpers
    # =========================
    def _clean_soup(self, soup: BeautifulSoup):
        for tag in soup(["script", "style", "nav", "footer", "aside", "noscript"]):
            tag.decompose()
        return soup

    def _extract_text(self, soup: BeautifulSoup) -> str:
        text = soup.get_text(separator="\n", strip=True)
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        return "\n".join(chunk for chunk in chunks if chunk)

    def _extract_links(self, soup: BeautifulSoup, base_url: str):
        links = []
        for a in soup.find_all("a", href=True):
            text = a.get_text(strip=True)
            href = urljoin(base_url, a["href"])
            if text and href.startswith("http"):
                links.append({
                    "text": text,
                    "url": href
                })
        return links

    # =========================
    # Requests-based scraping
    # =========================
    def scrape_with_requests(self, url: str):
        try:
            response = requests.get(url, headers=self.headers, timeout=12)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "lxml")
            soup = self._clean_soup(soup)

            content = self._extract_text(soup)
            links = self._extract_links(soup, url)

            title = soup.title.string.strip() if soup.title else "No title found"
            meta_desc = soup.find("meta", attrs={"name": "description"})
            description = meta_desc["content"].strip() if meta_desc else "No description"

            return {
                "success": True,
                "title": title,
                "description": description,
                "content": content,
                "links": links,
                "method": "requests"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": "requests"
            }

    # =========================
    # Selenium-based scraping
    # =========================
    def scrape_with_selenium(self, url: str):
        driver = None
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument(f"user-agent={self.headers['User-Agent']}")

            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            driver.get(url)
            WebDriverWait(driver, 12).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            time.sleep(2)

            soup = BeautifulSoup(driver.page_source, "lxml")
            soup = self._clean_soup(soup)

            content = self._extract_text(soup)
            links = self._extract_links(soup, url)

            title = driver.title or "No title found"
            meta_desc = soup.find("meta", attrs={"name": "description"})
            description = meta_desc["content"].strip() if meta_desc else "No description"

            return {
                "success": True,
                "title": title,
                "description": description,
                "content": content,
                "links": links,
                "method": "selenium"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": "selenium"
            }

        finally:
            if driver:
                driver.quit()

    # =========================
    # Public API
    # =========================
    def scrape(self, url: str, use_selenium: bool = False):
        """
        Main entry point.
        Tries requests first unless Selenium is forced.
        """
        if use_selenium:
            return self.scrape_with_selenium(url)

        result = self.scrape_with_requests(url)

        if not result["success"] or len(result.get("content", "")) < 200:
            return self.scrape_with_selenium(url)

        return result
