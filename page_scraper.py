import requests
import cchardet
import lxml
from bs4 import BeautifulSoup
from typing import List, Tuple
import bs4
from multiprocessing import Pool


class WikiPageScraper:    
    def __init__(self, min_n_chars: int = 128, n_processes: int = 2):
        """
        Scrapes a Wikipedia article page. 
        It only extracts paragraphs' text (no tables or list).

        Parameters
        ----------
        min_n_chars : int, optional
            Minimum number of characters in a paragraph, by default 128
        n_processes : int, optional
            Number of processes to run, by default 2
        """
        assert min_n_chars >= 0
        self.min_n_chars = min_n_chars
        self.n_processes = n_processes
        
    def run(self, pages: List[str]) -> List[dict]:
        stride = (len(pages) + self.n_processes - 1) // self.n_processes
        pages = [pages[i: i + stride] for i in range(0, len(pages), stride)]
        
        with Pool(self.n_processes) as p:
            scraped_pages = p.map(self.scrape_pages, pages)
            
        scraped_pages_ = scraped_pages[0]
        for pages_list in scraped_pages:
            scraped_pages_.extend(pages_list)
        return scraped_pages_
    
    def scrape_pages(self, page_urls: List[str]) -> List[dict]:
        session = requests.Session()
        scraped_pages = []
        for url in page_urls:
            req = session.get(url)
            scraped_page = self.scrape_page(req)
            if len(scraped_page['text']) > 0:
                scraped_pages.append(scraped_page)
        return scraped_pages
    
    def scrape_page(self, page: requests.models.Response) -> dict:
        soup = BeautifulSoup(page.text, 'lxml')
        
        title = soup.find(id='firstHeading').text
        content = soup.find_all('div', class_='mw-parser-output')[-1]
        
        return {'title': title, 'text': self.extract_text(content)}
    
    def extract_text(self, content: bs4.element.Tag) -> List[str]:
        paragraphs = content.findAll('p')
        text = []
        for p in paragraphs:
            paragraph_text = ''.join([elem.text for elem in p.contents]).strip()
            
            if len(paragraph_text) > self.min_n_chars:
                text.append(paragraph_text)
                
        return text

    
    
    
