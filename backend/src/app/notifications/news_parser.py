import aiohttp

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

from database.db_psql import AsyncSession, async_db_session
from src.app.notifications.crud.crud_news import news_dao
from src.app.notifications.schema.news import CreateNewsSchema


urls_to_monitor = [
    'https://economist.kg/',
    'https://www.turmush.kg/',
    'https://24.kg/',
    'https://kaktus.media/',
    'https://www.super.kg/',
    'https://www.tazabek.kg/',
    'https://vesti.kg/',
    'https://kyrgyz.mid.ru/ru/'
]

class NewsParser:
    def __init__(self, urls):
        self.urls = urls
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.latest_news = {}

    async def fetch(self, session, url):
        async with session.get(url, headers=self.headers) as response:
            return await response.text()

    async def parse_economist_kg(self, html, base_url):
        soup = BeautifulSoup(html, 'html.parser')
        news_items = soup.select('a.gh-card-title-link')
        news = []
        for item in news_items[:2]:
            title = item.get('aria-label').strip() # type: ignore
            link = urljoin(base_url, item['href']) # type: ignore
            news.append({'title': title, 'link': link, 'date': datetime.now()})
        return news

    async def parse_turmush_kg(self, html, base_url):
        soup = BeautifulSoup(html, 'html.parser')
        news_items = soup.select('div.card-body a.text-light')
        news = []
        for item in news_items[:2]:
            title = item.select_one('h5.card-title').get_text(strip=True) # type: ignore
            link = urljoin(base_url, item['href']) # type: ignore
            news.append({'title': title, 'link': link, 'date': datetime.now()})
        return news
    
    async def parse_24_kg(self, html, base_url):
        soup = BeautifulSoup(html, 'html.parser')
        news_items = soup.select('.one .title a')
        news = []
        for item in news_items[:2]:
            title = item.get_text(strip=True)
            link = urljoin(base_url, item['href']) # type: ignore
            news.append({'title': title, 'link': link, 'date': datetime.now()})
        return news

    async def parse_kaktus_media(self, html, base_url):
        soup = BeautifulSoup(html, 'html.parser')
        news_items = soup.select('div.Dashboard-Content-Card a.Dashboard-Content-Card--name')
        news = []
        for item in news_items[:4]:
            title = item.get_text(strip=True)
            link = urljoin(base_url, item['href']) # type: ignore
            news.append({'title': title, 'link': link, 'date': datetime.now()})
        return news

    async def parse_super_kg(self, html, base_url):
        soup = BeautifulSoup(html, 'html.parser')
        news_items = soup.select('.section-list-item-title a')
        news = []
        for item in news_items[:2]:
            title = item.get_text(strip=True)
            link = urljoin(base_url, item['href']) # type: ignore
            news.append({'title': title, 'link': link, 'date': datetime.now()})
        return news
    
    async def parse_tazabek_kg(self, html, base_url):
        soup = BeautifulSoup(html, 'html.parser')
        news_items = soup.select('.news_title a')
        news = []
        for item in news_items[:2]:
            title = item.get_text(strip=True)
            link = urljoin(base_url, item['href']) # type: ignore
            news.append({'title': title, 'link': link, 'date': datetime.now()})
        return news

    async def parse_vesti_kg(self, html, base_url):
        soup = BeautifulSoup(html, 'html.parser')
        news_items = soup.select('h4.nspHeader a')
        news = []
        for item in news_items[:2]:
            title = item.get('title').strip() # type: ignore
            link = urljoin(base_url, item['href']) # type: ignore
            news.append({'title': title, 'link': link, 'date': datetime.now()})
        return news

    async def parse_kyrgyz_mid_ru(self, html, base_url):
        soup = BeautifulSoup(html, 'html.parser')
        
        news_items = soup.select('div.news-photo a.news-photo__title')
        news_items += soup.select('div.news-tiles__item a.news-tiles__title')
        
        news = []
        for item in news_items[:5]:
            title = item.get_text(strip=True)
            link = urljoin(base_url, item['href']) # type: ignore
            news.append({'title': title, 'link': link, 'date': datetime.now()})
        
        return news

    async def parse(self, url, html):
        if 'economist.kg' in url:
            return await self.parse_economist_kg(html, url)
        elif 'turmush.kg' in url:
            return await self.parse_turmush_kg(html, url)
        elif '24.kg' in url:
            return await self.parse_24_kg(html, url)
        elif 'kaktus.media' in url:
            return await self.parse_kaktus_media(html, url)
        elif 'super.kg' in url:
            return await self.parse_super_kg(html, url)
        elif 'tazabek.kg' in url:
            return await self.parse_tazabek_kg(html, url)
        elif 'vesti.kg' in url:
            return await self.parse_vesti_kg(html, url)
        elif 'kyrgyz.mid.ru' in url:
            return await self.parse_kyrgyz_mid_ru(html, url)
        else:
            return []

    async def get_news(self):
        async with aiohttp.ClientSession() as session:
            results = {}
            for url in self.urls:
                try:
                    html = await self.fetch(session, url)
                    news = await self.parse(url, html)
                    if news:
                        results[url] = news
                except Exception as e:
                    results[url] = f"Error fetching or parsing {url}: {e}"
            return results

    async def check_for_new_news(self, db:AsyncSession):
        new_news_found = []
        news_data = await self.get_news()
        for url, news_list in news_data.items():
            if isinstance(news_list, list):
                for news in news_list:
                    if await news_dao.get_by_title(db,news['title']):
                        continue
                    new_news_found.append(CreateNewsSchema(
                        title=news['title'],
                        url=url,
                        link=news['link']
                    ))
        return new_news_found

    async def run(self):
        async with async_db_session.begin() as db:
            new_news = await self.check_for_new_news(db)
            if new_news:
                for news in new_news:
                    await news_dao.create(db,news)



parser = NewsParser(urls=urls_to_monitor)