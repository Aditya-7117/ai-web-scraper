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
import re


class WebParser:
    """Handle web scraping with both BeautifulSoup and Selenium"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_with_requests(self, url):
        """Scrape static websites using requests and BeautifulSoup"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "aside"]):
                script.decompose()
            
            # Extract text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Extract metadata
            title = soup.title.string if soup.title else "No title found"
            meta_desc = soup.find("meta", attrs={"name": "description"})
            description = meta_desc["content"] if meta_desc else "No description"
            
            return {
                'success': True,
                'title': title,
                'description': description,
                'content': text,
                'method': 'requests'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'requests'
            }
    
    def scrape_with_selenium(self, url):
        """Scrape dynamic websites using Selenium"""
        driver = None
        try:
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument(f'user-agent={self.headers["User-Agent"]}')
            
            # Initialize driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Load page
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(2)
            
            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'lxml')
            
            # Remove unwanted elements
            for element in soup(["script", "style", "nav", "footer", "aside"]):
                element.decompose()
            
            # Extract text
            text = soup.get_text(separator='\n', strip=True)
            
            # Clean text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Extract metadata
            title = driver.title or "No title found"
            meta_desc = soup.find("meta", attrs={"name": "description"})
            description = meta_desc["content"] if meta_desc else "No description"
            
            return {
                'success': True,
                'title': title,
                'description': description,
                'content': text,
                'method': 'selenium'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'method': 'selenium'
            }
        
        finally:
            if driver:
                driver.quit()
    
    def scrape(self, url, use_selenium=False):
        """Main scraping method - tries requests first, falls back to Selenium"""
        if use_selenium:
            return self.scrape_with_selenium(url)
        
        # Try requests first (faster)
        result = self.scrape_with_requests(url)
        
        # If requests fails or content is too short, try Selenium
        if not result['success'] or len(result.get('content', '')) < 100:
            return self.scrape_with_selenium(url)
        
        return result
    
    def extract_links(self, url):
        """Extract all links from a page"""
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'lxml')
            
            links = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('http'):
                    links.append({
                        'url': href,
                        'text': link.get_text(strip=True)
                    })
            
            return links
        except Exception as e:
            return []