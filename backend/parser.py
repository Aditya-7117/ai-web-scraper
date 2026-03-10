import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin


class WebParser:
    """
    Universal Web Scraper

    Supports:
    - Static scraping (requests + BeautifulSoup)
    - Dynamic scraping (Selenium headless browser)
    - Text extraction
    - Hyperlink extraction for RAG grounding
    """

    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

    # --------------------------------------------------
    # Cleaning utilities
    # --------------------------------------------------
    def _clean_soup(self, soup: BeautifulSoup):
        for tag in soup(["script", "style", "nav", "footer", "aside", "noscript"]):
            tag.decompose()
        return soup

    def _extract_text(self, soup: BeautifulSoup):
        text = soup.get_text(separator="\n", strip=True)
        return "\n".join(line.strip() for line in text.splitlines() if line.strip())

    def _extract_links(self, soup: BeautifulSoup, base_url):
        links = []

        for a in soup.find_all("a", href=True):
            href = urljoin(base_url, a["href"])
            text = a.get_text(strip=True)

            if href.startswith("http") and text:
                links.append({
                    "text": text,
                    "url": href
                })

        return links

    # --------------------------------------------------
    # Static Scraping
    # --------------------------------------------------
    def scrape_with_requests(self, url):

        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")
            soup = self._clean_soup(soup)

            content = self._extract_text(soup)
            links = self._extract_links(soup, url)

            title = soup.title.string.strip() if soup.title else "No title"
            meta = soup.find("meta", attrs={"name": "description"})
            description = meta["content"].strip() if meta else "No description"

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

    # --------------------------------------------------
    # Dynamic Scraping (Selenium)
    # --------------------------------------------------
    def scrape_with_selenium(self, url):

        driver = None

        try:

            chrome_options = Options()
            chrome_options.add_argument("--headless=new")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")

            # Built-in Chrome driver manager (stable)
            driver = webdriver.Chrome(options=chrome_options)

            driver.get(url)

            html = driver.page_source

            soup = BeautifulSoup(html, "lxml")
            soup = self._clean_soup(soup)

            content = self._extract_text(soup)
            links = self._extract_links(soup, url)

            title = driver.title
            meta = soup.find("meta", attrs={"name": "description"})
            description = meta["content"].strip() if meta else "No description"

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
    # --------------------------------------------------
    # Main entry
    # --------------------------------------------------
    def scrape(self, url, use_selenium=False):

        if use_selenium:
            return self.scrape_with_selenium(url)

        result = self.scrape_with_requests(url)

        if not result["success"] or len(result["content"]) < 200:
            return self.scrape_with_selenium(url)

        return result