import scrapy
from scrapy.loader import ItemLoader
from ..items import ArticleItem
import pymongo
from ..utils import already_scraped

class VnexpressSpider(scrapy.Spider):
    name = "vnexpress"
    allowed_domains = ["vnexpress.net"]
    already_scraped_urls = []

    END_PAGE = 20 #20  tầm nửa năm trước

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.already_scraped_urls = already_scraped()

    def start_requests(self):
        start_urls = [f'https://vnexpress.net/kinh-doanh/ebank-p1']
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'template': url, 'page': 1})

    def parse(self, response):
        print(f"Scraping page {response.meta['page']} of {response.url}")

        articles = response.xpath("//article[@class='item-news item-news-common thumb-left' or @class='item-news full-thumb article-topstory']")
        for article in articles:
            loader = ItemLoader(item=ArticleItem(), selector=article, response=response)

            loader.add_value('source', self.name)

            abs_url = article.xpath(".//a/@href").extract_first()
            loader.add_value('url', abs_url)
            if abs_url in self.already_scraped_urls:
                print(f"Already scraped {abs_url}")
                continue

            self.already_scraped_urls.append(abs_url)
            yield scrapy.Request(url=abs_url, callback=self.parse_summary, meta={'loader': loader})
            # break
        cur_page = response.meta['page']
        if cur_page < self.END_PAGE:
            cur_page += 1
            next_page = response.meta['template'].replace(f'-p{cur_page - 1}', f'-p{cur_page}')
            yield scrapy.Request(url=next_page, callback=self.parse, meta={'template': next_page, 'page': cur_page})

    def parse_summary(self, response):
        loader = response.meta['loader']
        loader.selector = response

        loader.add_xpath('title', "//h1[@class='title-detail']/text()")

        time = response.xpath("//span[@class='date']/text()").extract_first()
        if time is not None:
            time = time.split(',')
            day = time[1].strip()
            hour = time[-1].strip().split(' ')[0]
            loader.add_value('time', f"{day} - {hour}")

        loader.add_xpath('author', "//p[@class='author_mail' or (@class='Normal' and @style='text-align:right;') or @class='people mt-30' or (@class='Normal' and @align='right')]/strong/text() | //div[@class='people mt-30']/p/strong/text()")
        loader.add_value('category', 'Kinh doanh/ebank')

        paragraphs = response.xpath("//p[(@class='Normal' or @class='description') and not(@style='text-align:right;')] | //div[contains(@class, 'section-inner') or @class='WordSection1']/p")
        text = []
        for p in paragraphs:
            content = p.xpath(".//text()[not(parent::script)]").extract()
            content = [c.strip() for c in content if c.strip()]
            content = ' '.join(content).strip()
            if content:
                text.append(content)
        loader.add_value('text', text)

        text = response.xpath("//p[@class='Normal']/text()").extract_first()
        if time is None and text is None:
            loader.add_xpath('text', "//div[@id='longform']//p//text()")

        yield loader.load_item()