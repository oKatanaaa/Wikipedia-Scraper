import requests
import cchardet
import lxml
import traceback
from bs4 import BeautifulSoup
from typing import List, Optional, Tuple
import bs4
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
import os
from .utils import infer_folder_name
from time import sleep


class WikiPageScraperV2:    
    """
    Same as WikiPageScraper, but starts multiple threads in each process accelerating things a little (about 10%).
    """
    def __init__(self, min_n_chars: int = 128, n_processes: int = 2, n_threads_per_process: int = 2, save_folder: Optional[str] = None):
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
        self.n_threads_per_process = n_threads_per_process
        self.save_folder = save_folder
        self.title_cache = set()
        
    def run(self, pages: List[str], pool: Optional[Pool] = None) -> List[dict]:  # type: ignore
        stride = (len(pages) + self.n_processes - 1) // self.n_processes
        pages: List[List[str]] = [pages[i: i + stride] for i in range(0, len(pages), stride)]  # type: ignore
        
        is_local = False
        if pool is None:
            is_local = True
            pool = Pool(self.n_processes)
            
        scraped_pages = pool.map(self.scrape_pages, pages)
        
        if is_local:
            pool.close()

        scraped_pages_ = []
        titles = set()
        for pages_list in scraped_pages:
            for page in pages_list:
                if not page['title'] in titles:
                    scraped_pages_.append(page)
                    titles.add(page['title'])
        return scraped_pages_
    
    def scrape_pages(self, page_urls: List[str]) -> List[dict]:
        session = requests.Session()
        scraped_pages = []
        
        def scrape(url):
            req = session.get(url)
            # Status code 429 means too many requests, need to wait a little
            while req.status_code == 429:
                sleep(0.01)
                req = session.get(url)
                
            if req.status_code != 200:
                print(f'Could not retrieve page from {url}. Code: {req.status_code}. Reason: {req.reason}')
                return
            
            scraped_page = self.scrape_page(req)
            
            if len(scraped_page['text']) == 0:
                return
            
            scraped_pages.append(scraped_page)
            
            if self.save_folder is not None:
                # We have to split article files among different folder
                # because we may hit the storage limit (65000 files max in one folder).
                # Here we take the first 2 characters of the article title and use it as 
                # folder name.
                folder_name = infer_folder_name(scraped_page['title'])
                os.makedirs(os.path.join(self.save_folder, folder_name), exist_ok=True)
                filename = os.path.join(
                    self.save_folder, 
                    folder_name,
                    f"{scraped_page['title'].replace('/', '')}.txt"
                )
                with open(filename, 'w') as f:
                    f.write('\n\n'.join(scraped_page['text']))
        
        with ThreadPool(self.n_threads_per_process) as p:
            p.map(scrape, page_urls)
        
        return scraped_pages
    
    def scrape_page(self, page: requests.models.Response) -> dict:
        soup = BeautifulSoup(page.text, 'lxml')
        
        heading = soup.find(id='firstHeading')
        title = page.url.split('/')[-1] if heading is None else heading.text  # type: ignore
        
        if title in self.title_cache:
            return {'title': title, 'text': ''}
        else:
            self.title_cache.add(title)
        
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

    
    
    
