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

pages = page_scraper.run(['https://en.wikipedia.org/wiki/Aa.'])

pages
# Output:
#[{'title': 'Intercostal arteries',
#  'text': ['. The latter gives out the remaining anterior intercostal branches. Two in number in each space, these small vessels pass lateralward, one lying near the lower margin of the',
#   'It gives off intercostal branches to the seventh, eighth, and ninth intercostal spaces; these diminish in size as the spaces decrease in length, and are distributed in a manner precisely similar to the intercostal arteries from the',
#   'The right aortic intercostals are longer than the left because of the position of the aorta on the left side of the vertebral column; they pass across the bodies of the',
#   'of the given space.  The vein is superior to the artery, and the intercostal nerve is inferior to it. Commonly, the mnemonic, "Van," is used to recall the order of the vein, artery and nerve, from superior to inferior.']}]
```

There is a Jupyter Notebook called `playground.ipynb`. Take a look and play a little with the scraper.
