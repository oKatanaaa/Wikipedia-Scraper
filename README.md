### Wikipedia Scraper

This repo contains a simple Wikipedia scraper that allows to downloads a huge pile of text. It uses `requests` to download pages and `BeautifulSoup` to parse them.

I know that there is a publicly available Wikipedia dataset (https://huggingface.co/datasets/wikipedia), I just wanted to try out scraping. It turned out to be pretty easy (and fun!).

The code is somewhat optimized (`BeautifulSoup` uses `lxml` parser and `cchardet` library and some other minor tweaks), so you can use to get lots of text in a reasonable amount of time.

This project is in progress. Later I'll add some helper scripts so that you can call the scraper from terminal and get data in one command.

### Scripts

#### WikiLinksScraper

This class is used for scraping a list of Wikipedia article links.

```python
from links_scraper import WikiLinksScraper

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

This class is used to scrape the actual articles.

```python
from page_scraper import WikiPageScraper

page_scraper = WikiPageScraper(n_processes=1)

pages = page_scraper.run(['https://en.wikipedia.org/wiki/Aa._intercostales'])

pages[0]
# Output:
#{'title': 'Intercostal arteries',
# 'text': ['The intercostal arteries are a group of arteries that supply the area between the ribs ("costae"), called the intercostal space. The highest intercostal artery (supreme intercostal artery or superior intercostal artery) is an artery in the human body that usually gives rise to the first and second posterior intercostal arteries, which supply blood to their corresponding intercostal space.  It usually arises from the costocervical trunk, which is a branch of the subclavian artery.  Some anatomists may contend that there is no supreme intercostal artery, only a supreme intercostal vein.', ...
```

There is a Jupyter Notebook called `playground.ipynb`. Take a look and play a little with the scraper.
