import scrapy
from scrapy.loader import ItemLoader
from ..items import ArticleItem
import pymongo
import json
from ..utils import already_scraped

class KinhtedothiSpider(scrapy.Spider):
    name = "kinhtedothi"
    allowed_domains = ["kinhtedothi.vn"]
    already_scraped_urls = []

    START_PAGE = 1
    END_PAGE = 1388 # 1388  đến 16/05/2022

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.already_scraped_urls = already_scraped()

    def start_requests(self):
        urls = [
            f'https://kinhtedothi.vn/api/category/1212092406/paging/{self.START_PAGE}',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print(f"Scraping page {self.START_PAGE}")
        json_data = json.loads(response.body)
        for article in json_data:
            loader = ItemLoader(item=ArticleItem(), response=response)

            loader.add_value('source', self.name)
            loader.add_value('category', article['CatName'])
            loader.add_value('summary', article['Sapo'].split('Kinhtedothi - ')[-1])
            loader.add_value('title', article['Title'])
            
            time = article['PublishedDate']
            day = time.split('T')[0].replace('-', '/')
            hour = time.split('T')[1].split(':')[:2]
            day = day.split('/')[::-1]
            day = '/'.join(day)
            loader.add_value('time', f"{day} - {hour[0]}:{hour[1]}")

            abs_url = 'https://kinhtedothi.vn' + article['Url'] 
            loader.add_value('url', abs_url)
            if abs_url in self.already_scraped_urls:
                print(f"Already scraped {abs_url}")
                continue

            self.already_scraped_urls.append(abs_url)
            yield scrapy.Request(url=abs_url, callback=self.parse_summary, meta={'loader': loader})
            # break

        if self.START_PAGE < self.END_PAGE:
            self.START_PAGE += 1
            next_page = f'https://kinhtedothi.vn/api/category/1212092406/paging/{self.START_PAGE}'
            yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_summary(self, response):
        loader = response.meta['loader']
        loader.selector = response

        paragraphs = response.xpath("//div[contains(@itemprop, 'articleBody')]//p")
        text = []
        for p in paragraphs:
            content = p.xpath(".//text()").extract()
            content = [c.strip() for c in content if c.strip()]
            content = ' '.join(content).strip()
            if content:
                text.append(content)
        loader.add_value('text', text)

        loader.add_xpath('author', "//span[@class='detail__author']/text()")

        yield loader.load_item()
