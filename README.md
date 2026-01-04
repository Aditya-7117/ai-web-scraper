\# AI Web Scraper \& Analyzer



An AI-powered web scraping application that extracts content from websites and enables semantic analysis using Large Language Models.



\## Features

\- Static \& dynamic website scraping

\- Selenium-based rendering

\- AI-powered summarization and Q\&A

\- Streamlit interactive UI



\## Tech Stack

\- Python

\- Selenium, BeautifulSoup

\- Streamlit

\- Gemini LLM



\## How to Run



```bash

pip install -r requirements.txt

streamlit run app.py

```



\## Architecture Flow

1\. User provides website URL

2\. Dynamic/static content is scraped using Requests/Selenium

3\. Content is cleaned and parsed

4\. LLM performs semantic analysis (summary, Q\&A, insights)

5\. Results displayed via Streamlit UI



\## Screenshots



\### Home

!\[Home](screenshots/home.png)



\### Scraped Content

!\[Scrape](screenshots/scrape\_result.png)



\### AI Summary

!\[Summary](screenshots/ai\_summary.png)



\## Security Note

\- No API keys are stored in code

\- Users provide their own LLM API keys per session



