from typing import List, Optional
from .links_scraper_iter import WikiLinksScraperIter
from .page_scraper_v2 import WikiPageScraperV2
import argparse
import os
from multiprocessing import Pool


DEFAULT_N_PROCESSES = 4
DEFAULT_N_THREADS = 4
DEFAULT_STRIDE = 2
DEFAULT_MAX_LINKS_PER_INDEX = 100
DEFAULT_MIN_CHARS = 512
DEFAULT_BATCH_SIZE = 128


def main(links_scraper: WikiLinksScraperIter, page_scraper: WikiPageScraperV2, batch_size: int, indices: Optional[List[str]]):
    links_scraper.run_async(indices=indices)
    it = links_scraper.make_iterator()
    pool = Pool(page_scraper.n_processes)
    batch = []
    for link in it:
        if len(batch) < batch_size:
            batch.append(link)
            continue
        
        page_scraper.run(batch, pool=pool)
        batch = []
    
    if len(batch) > 0:
        page_scraper.run(batch)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='Wikipedia Scraper',
        description='Scrapes text from Wikipedia articles and saves them in txt files (`article name`.txt) in the specified directory.')
    parser.add_argument('-np', '--n_processes', type=int, help=f'Number of processes (page scraper). Default: {DEFAULT_N_PROCESSES}',
                        default=DEFAULT_N_PROCESSES)
    parser.add_argument('-nt', '--n_threads', type=int, help=f'Number of threads (links scraper). Default: {DEFAULT_N_THREADS}',
                        default=DEFAULT_N_THREADS)
    parser.add_argument('-s', '--save_folder', type=str, help='Save folder path.')
    parser.add_argument('-st', '--stride', type=int, help=f'Scrape only each `stride`th link. Default: {DEFAULT_STRIDE}',
                        default=DEFAULT_STRIDE)
    parser.add_argument('-max_l', '--max_links_per_index', type=int, help=f'Maximum number of links per index to scrape. Default: {DEFAULT_MAX_LINKS_PER_INDEX}',
                        default=DEFAULT_MAX_LINKS_PER_INDEX)
    parser.add_argument('-min_c', '--min_chars', type=int, help='Minimum number of characters per paragraph. ' + \
                        f'Paragraphs with fewer characters are skipped. Default: {DEFAULT_MIN_CHARS}', default=DEFAULT_MIN_CHARS)
    parser.add_argument('-bs', '--batch_size', type=int, help=f'Links are grouped in batches and then scraped in multiple processes. Default: {DEFAULT_BATCH_SIZE}',
                        default=DEFAULT_BATCH_SIZE)
    parser.add_argument('-ind', '--indices', type=str, help='Indices to scrape from. Example: Aa,Ba,Ca', default=None)
    
    args = parser.parse_args()
    
    links_scraper = WikiLinksScraperIter(
        stride=args.stride, n_max_links_per_index=args.max_links_per_index, 
        n_threads=args.n_threads
    )
    page_scraper = WikiPageScraperV2(
        min_n_chars=args.min_chars, n_processes=args.n_processes, 
        n_threads_per_process=2, save_folder=args.save_folder
    )
    
    os.makedirs(args.save_folder, exist_ok=True)
    indices = args.indices.split(',') if args.indices is not None else None
    main(links_scraper, page_scraper, args.batch_size, indices)
