import scrapy
from scrapy.loader import ItemLoader
from ..items import ArticleItem
import pymongo
from ..utils import already_scraped

class NhadautuSpider(scrapy.Spider):
    name = "nhadautu"
    allowed_domains = ["nhadautu.vn"]
    already_scraped_urls = []

    START_PAGE = 1
    END_PAGE = 951 # 951    đến 25/03/2017

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.already_scraped_urls = already_scraped()

    def start_requests(self):
        urls = [
            f'https://nhadautu.vn/?mod=news&act=loadmore&dev=1&page={self.START_PAGE}&cat_id=3'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print(f"Scraping page {self.START_PAGE}")
        articles = response.xpath("//li")

        for article in articles:
            loader = ItemLoader(item=ArticleItem(), selector=article, response=response)

            loader.add_value('source', self.name)
            loader.add_xpath('title', "./a/@title")
            loader.add_xpath('summary', "./div/div[@class='sapo_news mar_top10']/text()")

            time = article.xpath("./div/div[@class='time_news mar_top15']/text()").extract_first()
            month = time.split(',')[0].split(' ')[1]
            day = time.split(',')[1].strip()
            year = time.split(',')[2].split('|')[0].strip()
            hour = time.split('|')[-1].strip()
            loader.add_value('time', f"{day}/{month}/{year} - {hour}")

            url = article.xpath("./a/@href").extract_first()
            abs_url = url
            loader.add_value('url', abs_url)
            if abs_url in self.already_scraped_urls:
                print(f"Already scraped {abs_url}")
                continue

            self.already_scraped_urls.append(abs_url)
            print(f"Scraping {abs_url}")
            yield scrapy.Request(url=abs_url, callback=self.parse_summary, meta={'loader': loader})
            # break
        if self.START_PAGE < self.END_PAGE:
            self.START_PAGE += 1
            next_page = f'https://nhadautu.vn/?mod=news&act=loadmore&dev=1&page={self.START_PAGE}&cat_id=3'
            yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_summary(self, response):
        loader = response.meta['loader']
        loader.selector = response

        paragraphs = response.xpath("//div[contains(@id, 'content_detail')]//p")
        text = []
        for p in paragraphs:
            content = p.xpath(".//text()").extract()
            content = [c.strip() for c in content if c.strip()]
            content = ' '.join(content).strip()
            if content:
                text.append(content)
        loader.add_value('text', text)

        loader.add_xpath('category', "//div[@class='breadcumb fl']/a/text()")
        loader.add_xpath('author', "//div[@class='box_infomation']/span[@class='f11']/text()")

        yield loader.load_item()
