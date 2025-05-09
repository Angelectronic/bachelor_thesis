import scrapy
from scrapy.loader import ItemLoader
from ..items import ArticleItem
import pymongo
from ..utils import already_scraped

class VietnambizSpider(scrapy.Spider):
    name = "vietnambiz"
    allowed_domains = ["vietnambiz.vn"]
    already_scraped_urls = []

    END_PAGE = 1426 # 1426  đến 22/08/2016

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.already_scraped_urls = already_scraped()

    def start_requests(self):
        urls = [
            f'https://vietnambiz.vn/tai-chinh/ngan-hang/trang-1.htm',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'template': url, 'page': 1})

    def parse(self, response):
        print(f"Scraping page {response.meta['page']} of {response.url}")

        articles = response.xpath("//div[@class='zone-pin-1' or @class='related-news'] | //div[@class='list-item']/div/div[@class='content']/h3 | //div[@class='list-news']/div[@class='item']")
        for article in articles:
            loader = ItemLoader(item=ArticleItem(), selector=article, response=response)

            loader.add_value('source', self.name)

            url = article.xpath("./a/@href").extract_first()
            abs_url = 'https://vietnambiz.vn' + url
            loader.add_value('url', abs_url)
            if abs_url in self.already_scraped_urls:
                print(f"Already scraped {abs_url}")
                continue

            self.already_scraped_urls.append(abs_url)
            yield scrapy.Request(url=abs_url, callback=self.parse_summary, meta={'loader': loader})
            # break
        if response.meta['page'] < self.END_PAGE:
            cur_page = response.meta['page'] + 1
            next_page = response.meta['template'].replace(f'trang-{cur_page - 1}', f'trang-{cur_page}')
            yield scrapy.Request(url=next_page, callback=self.parse, meta={'template': next_page, 'page': cur_page})

    def parse_summary(self, response):
        loader = response.meta['loader']
        loader.selector = response

        loader.add_xpath('title', "//h1[@data-role='title']/text()")
        loader.add_xpath('summary', "//div[@data-role='sapo']/text()")
        loader.add_xpath('category', "//a[@data-role='cate-name']/text()")

        time = response.xpath("//span[@data-role='publishdate']/text()").extract_first()
        time = time.split('|')
        loader.add_value('time', f'{time[1].strip()} - {time[0].strip()}')
        
        loader.add_xpath('author', "//p[@data-role='author']/text()")
        
        loader.add_xpath('origin', "//div[@class='link-source-full']/text()")

        paragraphs = response.xpath("//div[@data-role='content']//p")
        text = []
        for p in paragraphs:
            content = p.xpath(".//text()[not(ancestor::table | ancestor::figcaption)]").extract()
            content = [c.strip() for c in content if c.strip()]
            content = ' '.join(content).strip()
            if content:
                text.append(content)
        loader.add_value('text', text)

        yield loader.load_item()
