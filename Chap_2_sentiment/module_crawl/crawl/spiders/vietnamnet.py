import scrapy
from scrapy.loader import ItemLoader
from ..items import ArticleItem
from ..utils import already_scraped

class VietnamnetSpider(scrapy.Spider):
    name = "vietnamnet"
    allowed_domains = ["vietnamnet.vn"]
    start_urls = ["http://vietnamnet.vn/"]
    already_scraped_urls = []

    START_PAGE = 0
    END_PAGE = 3930 # 3930   đến 23/09/2010

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.already_scraped_urls = already_scraped()

    def start_requests(self):
        urls = [
            f'https://vietnamnet.vn/kinh-doanh-page{self.START_PAGE}'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print(f"Scraping page {self.START_PAGE}")

        articles = response.xpath("//div[contains(@class,'verticalPost ') or @class='horizontalPost__main']")
        for article in articles:
            loader = ItemLoader(item=ArticleItem(), selector=article, response=response)

            loader.add_value('source', self.name)

            url = article.xpath(".//h3/a/@href").extract_first() if article.xpath(".//h3/a/@href").extract_first() else article.xpath(".//a/@href").extract_first()
            if 'https://vietnamnet.vn' not in url:
                abs_url ='https://vietnamnet.vn' + url
            else:
                abs_url = url
            
            loader.add_value('url', abs_url)
            if abs_url in self.already_scraped_urls:
                print(f"Already scraped {abs_url}")
                continue

            self.already_scraped_urls.append(abs_url)
            yield scrapy.Request(url=abs_url, callback=self.parse_summary, meta={'loader': loader})
            # break
        if self.START_PAGE < self.END_PAGE:
            self.START_PAGE += 1
            next_page = f'https://vietnamnet.vn/kinh-doanh-page{self.START_PAGE}'
            yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_summary(self, response):
        loader = response.meta['loader']
        loader.selector = response

        loader.add_xpath('title', "//h1[@class='content-detail-title']/text()")
        loader.add_xpath('summary', "//h2[@class='content-detail-sapo sm-sapo-mb-0']//text()")

        time = response.xpath("//div[@class='bread-crumb-detail__time']/text()").extract_first()
        time = time.split(',')[-1].strip()
        loader.add_value('time', time)

        paragraphs = response.xpath("//div[contains(@class, 'maincontent main-content')]//p")
        text = []
        for p in paragraphs:
            content = p.xpath(".//text()").extract()
            content = [c.strip() for c in content if c.strip()]
            content = ' '.join(content).strip()
            if content:
                text.append(content)
        loader.add_value('text', text)
        
        author = response.xpath("//p[@class='article-detail-author__info']/span[@class='name']/a/@href").extract_first()
        if author:
            loader.add_value('author', 'https://vietnamnet.vn' + author)
        else:
            author = response.xpath("//div[@class='article-author-multiple__avatar']/a/@href").extract()
            author = ' và '.join('https://vietnamnet.vn' + a for a in author) if author else None
            loader.add_value('author', author)

            if not author:
                author = response.xpath("//div[contains(@class, 'content-detail')]//p/strong/text()").extract()
                author = author[-1].strip() if author else None
                loader.add_value('author', author)

        category = response.xpath("//div[@class='bread-crumb-detail sm-show-time']/ul/li/a/text()").extract()
        category = [c.strip() for c in category if c.strip()]
        category = '/'.join(category).strip()
        loader.add_value('category', category)

        yield loader.load_item()
