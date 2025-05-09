import scrapy
from scrapy.loader import ItemLoader
from ..items import ArticleItem
import pymongo
from ..utils import already_scraped
import requests

class CafefSpider(scrapy.Spider):
    name = "cafef"
    allowed_domains = ["cafef.vn"]
    already_scraped_urls = []
    
    START_PAGE = 1
    END_PAGE = 37179  #37179 đến 01/01/2000

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.already_scraped_urls = already_scraped()
    
    def start_requests(self):
        urls = [f'https://cafef.vn/doc-nhanh/trang-{self.START_PAGE}.chn']
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print(f"Scraping page {self.START_PAGE}")
        
        articles = response.xpath("//div[contains(@class, 'item')]")
        for article in articles:
            loader = ItemLoader(item=ArticleItem(), selector=article, response=response)

            loader.add_value('source', self.name)

            abs_url = "https://cafef.vn" + article.xpath(".//a[@class='news-title']/@href").extract_first()
            if abs_url in self.already_scraped_urls:
                print(f"Already scraped {abs_url}")
                continue
            self.already_scraped_urls.append(abs_url)

            loader.add_value('url', abs_url)

            yield scrapy.Request(url=abs_url, callback=self.parse_summary, meta={'loader': loader})

        if self.START_PAGE < self.END_PAGE:
            self.START_PAGE += 1
            next_page = f'https://cafef.vn/doc-nhanh/trang-{self.START_PAGE}.chn'
            yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_summary(self, response):
        loader = response.meta['loader']
        loader.selector = response

        loader.add_xpath('title', "//h1[@class='title']/text()")

        time = response.xpath("//span[@class='pdate']/text()").extract_first()
        time = time.split('-')
        day = time[0].strip()
        month = time[1].strip()
        year = time[2].strip()
        hour = time[3].strip().split(' ')[0]
        time = f"{day}/{month}/{year} - {hour}"
        loader.add_value('time', time)
        
        author = response.xpath("//p[@class='author']/text()").extract_first().split('Theo')[-1].strip()
        loader.add_value('author', author)

        loader.add_xpath('category', "//a[@class='category-page__name cat']/text()")
        
        paragraphs = response.xpath("//div[contains(@class, 'detail-content')]//p[not(ancestor::figure)]")
        text = []
        for p in paragraphs:
            content = p.xpath(".//text()").extract()
            content = [c.strip() for c in content if c.strip()]
            content = ' '.join(content).strip()
            if content:
                text.append(content)
        loader.add_value('text', text)

        origin = response.xpath("//span[@class='link-source-full']/text() | //span[contains(@class,'btn-copy-link-source')]/@data-link").extract_first().strip()
        if len(origin) == 0 or not origin or origin == '':
            idx = response.url.split('.chn')[0].split('-')[-1].strip()
            res = requests.get(f'https://sudo.cnnd.vn/Handlers/RequestHandler.ashx?c=getOrgUrl&newsId={idx}&channelId=4')
            origin = res.json()['Url'] if res.status_code == 200 else None
        if origin in self.already_scraped_urls:
            print(f"Already scraped {origin}")
            return
        loader.add_value('origin', origin)

        yield loader.load_item()