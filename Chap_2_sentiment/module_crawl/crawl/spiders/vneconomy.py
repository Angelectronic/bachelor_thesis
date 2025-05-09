import scrapy
from scrapy.loader import ItemLoader
from ..items import ArticleItem
from ..utils import already_scraped

class VneconomySpider(scrapy.Spider):
    name = "vneconomy"
    allowed_domains = ["vneconomy.vn"]
    already_scraped_urls = []

    START_PAGE = 1
    END_PAGE = 73  # 73    đến 12/07/2023

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.already_scraped_urls = already_scraped()
    
    def start_requests(self):
        urls = [
            f'https://vneconomy.vn/tai-chinh-ngan-hang.htm?trang={self.START_PAGE}'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print(f"Scraping page {self.START_PAGE}")
        articles = response.xpath("//article[@class='story story--featured story--timeline ']")
        for article in articles:
            loader = ItemLoader(item=ArticleItem(), selector=article, response=response)
            loader.add_value('source', self.name)

            abs_url = 'https://vneconomy.vn' + article.xpath(".//a/@href").extract_first()
            loader.add_value('url', abs_url)
            if abs_url in self.already_scraped_urls:
                print(f"Already scraped {abs_url}")
                continue

            self.already_scraped_urls.append(abs_url)
            yield scrapy.Request(url=abs_url, callback=self.parse_summary, meta={'loader': loader})

        if self.START_PAGE < self.END_PAGE:
            self.START_PAGE += 1
            next_page = f'https://vneconomy.vn/tieu-diem.htm?trang={self.START_PAGE}'
            yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_summary(self, response):
        loader = response.meta['loader']
        loader.selector = response

        loader.add_xpath('title', "//h1[@class='detail__title']/text()")
        loader.add_xpath('summary', "//h2[@class='detail__summary']//text()")

        time = response.xpath("//div[@class='detail__meta']/text()").extract_first()
        if time is not None:
            time = time.split('VnEconomy')[-1].split(' ')
            day = time[1].strip()
            hour = time[0].strip()
            loader.add_value('time', f"{day} - {hour}")
        else:
            time = response.xpath("//div[@class='detail__content']//p/strong/text()").extract_first()
            if time is not None:
                time = time.split('VnEconomy')[-1].split(' ')
                day = time[0].strip()
                hour = time[1].strip()
                loader.add_value('time', f"{day} - {hour}")


        loader.add_xpath('author', "//div[@class='detail__author']/strong/text()")
        loader.add_xpath('category', "//h1[@class='category-main']/a/text()")

        paragraphs = response.xpath("//div[@class='detail__content']//p")
        text = []
        for p in paragraphs:
            content = p.xpath(".//text()").extract()
            content = [c.strip() for c in content if c.strip()]
            content = ' '.join(content).strip()
            if content:
                text.append(content)
        loader.add_value('text', text)

        yield loader.load_item()
