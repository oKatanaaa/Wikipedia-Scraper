import requests
import cchardet
import lxml
from bs4 import BeautifulSoup
from typing import List, Tuple, Optional, Iterable
from multiprocessing import Pool
import string


class WikiLinksScraper:
    @staticmethod
    def get_SpecialAllPages_links(page: requests.models.Response) -> Tuple[List[str], str, str]:
        soup = BeautifulSoup(page.text, 'lxml')
        # Extract articles' links
        items = soup.find(class_='mw-allpages-chunk')
        hrefs = items.find_all('li', class_='allpagesredirect')  # type: ignore
        suffixes = map(lambda href: href.find('a').get('href'), hrefs)
        article_links = ['https://en.wikipedia.org' + s for s in suffixes]
        
        # Extract prev/next pages' links
        prev_pageA, next_pageA = soup.find_all(class_='mw-allpages-nav')[0].find_all('a')
        prev_page_link = 'https://en.wikipedia.org' + prev_pageA.get('href')
        next_page_link = 'https://en.wikipedia.org' + next_pageA.get('href')
        return article_links, prev_page_link, next_page_link
    
    
    def __init__(self, stride: int = 5, n_max_links_per_index: int = 20000, n_processes: int = 2):
        """
        Scrapes links from the A-Z index (https://en.wikipedia.org/wiki/Wikipedia:Contents/A%E2%80%93Z_index).

        Parameters
        ----------
        stride : int, optional
            Take every `stride`th link from the list of scraped links, by default 5
        n_max_links_per_index : int, optional
            Maximum number of links per index row (example, from Aa to AZ), by default 20000
        n_processes : int, optional
            Number of processes to run, by default 2
        """
        self.stride = stride
        self.n_max_links_per_index = n_max_links_per_index
        self.n_processes = n_processes
        
    def index_table_generator(self):
        for up_letter in string.ascii_uppercase:
            yield f'{up_letter}a'
        
    def run(self, indices: Optional[Iterable[str]] = None) -> List[str]:
        """
        Start links scraping.

        Parameters
        ----------
        indices : List[str], optional
            A list in indices which to scrape the links for, by default None

        Returns
        -------
        List[str]
            A list of scraped links.
        """
        if indices is None:
            indices = self.index_table_generator()
            
        with Pool(self.n_processes) as p:
            links = p.map(self.scrape_index, indices)
            
        links_ = links[0]
        for links_list in links:
            links_.extend(links_list)
        return links_

    def scrape_index(self, index: str) -> List[str]:
        req = requests.get(f'https://en.wikipedia.org/wiki/Special:AllPages/{index}')
        article_links, prev_page_link, next_page_link = WikiLinksScraper.get_SpecialAllPages_links(req)
        termination_link = article_links[0]
        article_links = article_links[::self.stride]
        session = requests.Session()
        while True:
            article_links_, prev_page_link, next_page_link = WikiLinksScraper.get_SpecialAllPages_links(session.get(next_page_link))
            if termination_link in article_links_ or len(article_links) >= self.n_max_links_per_index:
                # We've reached the end (encountered an article we already have) or the number
                # of links exceeded n_max_links.
                break
            
            article_links.extend(article_links_[::self.stride])
        return article_links
