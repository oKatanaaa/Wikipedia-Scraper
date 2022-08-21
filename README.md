### Wikipedia Scraper

This repo contains a simple Wikipedia scraper that allows to download a huge pile of text. It uses `requests` to download pages and `BeautifulSoup` to parse them.

I know there is a publicly available Wikipedia dataset (https://huggingface.co/datasets/wikipedia), I just wanted to try out scraping. It turned out to be pretty easy (and fun!).

The code is somewhat optimized (`BeautifulSoup` uses `lxml` parser and `cchardet` library and some other minor tweaks), so you can use to get lots of text in a reasonable amount of time.

### Scripts

#### WikiLinksScraper

This class is used for scraping a list of Wikipedia article links.

```python
from wiki_scraper import WikiLinksScraper

scraper = WikiLinksScraper(stride=10, n_max_links_per_index=10, n_processes=2)

links = scraper.run(['Aa', 'Ba'])

len(links), links[:4]
# Output: (25,
# ['https://en.wikipedia.org/wiki/Aa',
#  'https://en.wikipedia.org/wiki/Aa,_Brynjar',
#  'https://en.wikipedia.org/wiki/Aa.',
#  'https://en.wikipedia.org/wiki/Aa._intercostales'])
```

#### WikiPageScraper

This class is used to scrape the actual articles. Since different links may lead to the same page, there is a filtering logic inside the scraper, so don't be surprized if you get less scraped pages than there are links (some of them were duplicates or did not contain much text).

```python
from wiki_scraper import WikiPageScraper

page_scraper = WikiPageScraper(n_processes=1)

pages = page_scraper.run(['https://en.wikipedia.org/wiki/Aa._intercostales'])

pages[0]
# Output:
#{'title': 'Intercostal arteries',
# 'text': ['The intercostal arteries are a group of arteries that supply the area between the ribs ("costae"), called the intercostal space. The highest intercostal artery (supreme intercostal artery or superior intercostal artery) is an artery in the human body that usually gives rise to the first and second posterior intercostal arteries, which supply blood to their corresponding intercostal space.  It usually arises from the costocervical trunk, which is a branch of the subclavian artery.  Some anatomists may contend that there is no supreme intercostal artery, only a supreme intercostal vein.', ...
```

There is a Jupyter Notebook called `playground.ipynb`. Take a look and play a little with the scraper.

## Usage

### Installation

Run the following command:
```bash
pip install git+https://github.com/oKatanaaa/Wikipedia-Scraper
```

### Running

As a starting point, run the following to scrape a few articles:
```bash
python -m wiki_scraper.run -s articles
```
It will create an `articles` folder and fetch about a thousand files in a minute in it (depends on your internet connection and pc performance).

All arguments:
- `-np, --n_processes`. Number of processes to start within the page scraper. Default: 4.
- `-nt, --n_threads`. Number of threads to start within the link scraper. Default: 4.
- `-s, --save_folder`. Path to the folder where to save the articles.
- `-st, --stride`. Scrape only each `stride`th link. Default: 2 (meaning it'll take every second link). This argument controls data variety to some extent.
- `-max_l, --max_links_per_index`. Maximum number of links per index to scrape. Default: 100.
- `-min_c, --min_chars`. Minimum number of characters per paragraph. Paragraphs with fewer characters are skipped. Default: 512. I recommend to leave it as it is, but you may adjust it to your needs of course.
- `-bs, --batch_size`. Links are grouped in batches and then scraped in multiple processes. Default: 128. Lower the batch size - higher the string pickling overhead. 128 seems to be optimal.
- `-ind, --indices`. Indices to scrape from. Example: Aa,Ba,Ca. (if you don't get what indices are, check out this link https://en.wikipedia.org/wiki/Wikipedia:Contents/A%E2%80%93Z_index)

### FAQ

Q: How much of Wikipedia can I fetch with this?
A: Short answer: a lot. Long answer: it depends. 
In theory, the library itself can load all of Wikipedia articles (there is other stuff as well, but this all is only about articles), but not all them may be stored on your machine. Depending on your OS and data storage, you can store different number of files in a folder. Roughly speaking, 65000 for Linux and 10000 for Windows (physically you can store more, but there might be unexpected behaviour). Once you've reached the limit for your storage, system stops saving files.
Considering the worst case, you'll be able to fetch: 24 (letters) * 24 (letters) * 2 (upcase and lowercase) * 10000 (storage capacity) = 11_520_000. That's considering that articles are uniformly distributed among indices (Aa, Ab, ..., Zx, Zc, etc), which in all likelihood is not the case.

Q: How long does it take to fetch the data?
A: With default parameters it is roughly a minute for a thousand articles.
My configuration:
    - CPU: Ryzen 7 4800H (8 cores, 16 threads, 2.9 GHz).
    - SSD storage (don't know the speed, but believe it is fast).
    - WiFi Internet connection with about 50 MB/s speed.
Guess I'll add some more measurements later.

