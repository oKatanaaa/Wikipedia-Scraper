import requests
import cchardet
import lxml
from bs4 import BeautifulSoup
from typing import List, Tuple, Optional, Iterable
from threading import Thread
from multiprocessing.pool import ThreadPool
import string


class WikiLinksScraperIter:
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
    
    def __init__(self, stride: int = 5, n_max_links_per_index: int = 20000, n_threads: int = 2):
        """
        Scrapes links from the A-Z index (https://en.wikipedia.org/wiki/Wikipedia:Contents/A%E2%80%93Z_index).

        Parameters
        ----------
        stride : int, optional
            Take every `stride`th link from the list of scraped links, by default 5
        n_max_links_per_index : int, optional
            Maximum number of links per index row (example, from Aa to AZ), by default 20000
        n_threads : int, optional
            Number of threads to run, by default 2
        """
        self.stride = stride
        self.n_max_links_per_index = n_max_links_per_index
        self.n_threads = n_threads
        self.cache: List[List[str]] = []
        self.thread_finished_counter = 0
        self.fetching_pool: Optional[ThreadPool] = None
        
    def index_table_generator(self) -> Iterable[str]:
        for up_letter in string.ascii_uppercase:
            yield f'{up_letter}a'
        
    def run(self, indices: Optional[Iterable[str]] = None) -> List[str]:
        """
        Start links scraping.

        Parameters
        ----------
        indices : Iterable[str], optional
            An iterable of indices which to scrape the links for, by default None

        Returns
        -------
        List[str]
            A list of scraped links.
        """
        if indices is None:
            indices = self.index_table_generator()
        
        with ThreadPool(self.n_threads) as p:
            links = p.map(self.scrape_index, indices)
        
        links_ = links[0]
        for links_list in links:
            links_.extend(links_list)
        return links_

    def scrape_index(self, index: str) -> List[str]:
        req = requests.get(f'https://en.wikipedia.org/wiki/Special:AllPages/{index}')
        article_links, prev_page_link, next_page_link = WikiLinksScraperIter.get_SpecialAllPages_links(req)
        termination_link = article_links[0]
        article_links = article_links[::self.stride]
        self.cache.append(article_links[::self.stride])
        session = requests.Session()
        while True:
            article_links_, prev_page_link, next_page_link = WikiLinksScraperIter.get_SpecialAllPages_links(session.get(next_page_link))
            if termination_link in article_links_ or len(article_links) >= self.n_max_links_per_index:
                # We've reached the end (encountered an article we already have) or the number
                # of links exceeded n_max_links.
                break
            
            article_links_ = article_links_[::self.stride]
            article_links.extend(article_links_)
            
            self.cache.append(article_links_)

        self.thread_finished_counter += 1
            
        return article_links
    
    def run_async(self, indices=None):
        if indices is None:
            indices = self.index_table_generator()
        
        print('Create a pool')
        self.fetching_pool = ThreadPool(self.n_threads)
        self.fetching_pool.map_async(self.scrape_index, indices, callback=self.kill_pool)
        print('Pool has started')

    def make_iterator(self):
        while self.fetching_pool is not None or len(self.cache) != 0:
            if len(self.cache) == 0:
                continue
            
            for link in self.cache.pop():
                yield link

    def kill_pool(self, *args):
        if self.fetching_pool is None:
            raise RuntimeError('No fetching thread instance has been created yet.')
        
        self.fetching_pool.close()
        self.fetching_pool = None
        print('Data has been fetched, the pool is closed.')
    