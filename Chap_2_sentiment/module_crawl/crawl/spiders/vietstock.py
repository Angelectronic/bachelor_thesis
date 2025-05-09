import scrapy
from scrapy.loader import ItemLoader
from ..items import ArticleItem
from ..settings import DRIVER_NAME, SERVER_NAME, DATABASE_NAME
import datetime
from ..utils import already_scraped

class VietstockSpider(scrapy.Spider):
    name = "vietstock"
    allowed_domains = ["vietstock.vn"]
    already_scraped_urls = []

    START_PAGE = 1
    END_PAGE = 3236 # 3236    đến 02/07/2003
    cur_date = datetime.datetime.now().strftime('%Y-%m-%d')

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.already_scraped_urls = already_scraped()

    def start_requests(self):
        urls = [
            f'https://vietstock.vn/StartPage/ChannelContentPage?channelID=734&page={self.START_PAGE}&fromdate=2003-07-02&todate={self.cur_date}'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print(f"Scraping page {self.START_PAGE}")
        articles = response.xpath("//div[@class='single_post_text']")
        for article in articles:
            loader = ItemLoader(item=ArticleItem(), selector=article, response=response)

            loader.add_value('source', self.name)
            loader.add_xpath('category', ".//div[@class='meta3']/a/text()")

            url = article.xpath("./h4/a/@href").extract_first()
            abs_url ='https://vietstock.vn' + url
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
            next_page = f'https://vietstock.vn/StartPage/ChannelContentPage?channelID=734&page={self.START_PAGE}&fromdate=2018-01-01&todate={self.cur_date}'
            yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_summary(self, response):
        loader = response.meta['loader']
        loader.selector = response

        loader.add_xpath('title', "//h1[@class='article-title']/text()")
        loader.add_xpath('summary', "//p[@class='pHead']//text()")

        author = response.xpath("//p[@class='pAuthor']/text()").extract_first()
        if author is None:
            author = response.xpath("//p[@class='pAuthor']/a/@href").extract_first()
            if author:
                author = 'https://vietstock.vn' + author
        loader.add_value('author', author)

        origin = response.xpath("//p[@class='pSource']/a/@href").extract_first()
        if origin in self.already_scraped_urls:
            print(f"Already scraped {origin}")
            self.already_scraped_urls.append(origin)
            return
        loader.add_value('origin', origin)

        time = response.xpath("//span[@class='date']/text()").extract_first()
        time = time.replace(' ', ' - ')
        loader.add_value('time', time)

        paragraphs = response.xpath("//p[contains(@class, 'pBody')] | //div[@class='tdb-block-inner td-fix-index' or @id='vst_detail']//p[not(@class='pHead' or @class='pTitle')]")
        text = []
        for p in paragraphs:
            content = p.xpath(".//text()").extract()
            content = [c.strip() for c in content if c.strip()]
            content = ' '.join(content).strip()
            if content:
                text.append(content)
        loader.add_value('text', text)

        yield loader.load_item()
