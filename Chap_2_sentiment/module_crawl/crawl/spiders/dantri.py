import scrapy
from scrapy.loader import ItemLoader
from ..items import ArticleItem
import pymongo
from ..utils import already_scraped

class DantriSpider(scrapy.Spider):
    name = "dantri"
    allowed_domains = ["dantri.com.vn"]
    already_scraped_urls = []

    END_PAGE = 30  # 30 tầm nửa năm trước

    def __init__(self, name=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.already_scraped_urls = already_scraped()
    
    def start_requests(self):
        urls = [
            f'https://dantri.com.vn/kinh-doanh/tai-chinh/trang-1.htm',
            f'https://dantri.com.vn/kinh-doanh/chung-khoan/trang-1.htm',
            f'https://dantri.com.vn/kinh-doanh/doanh-nghiep/trang-1.htm',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'template': url, 'page': 1})

    def parse(self, response):
        print(f"Scraping page {response.meta['page']} of {response.url}")
        articles = response.xpath("//article[@class='article-item']")
        for article in articles:
            loader = ItemLoader(item=ArticleItem(), selector=article, response=response)
            loader.add_value('source', self.name)

            abs_url = 'https://dantri.com.vn' + article.xpath(".//a/@href").extract_first()
            loader.add_value('url', abs_url)
            if abs_url in self.already_scraped_urls:
                print(f"Already scraped {abs_url}")
                continue

            self.already_scraped_urls.append(abs_url)
            yield scrapy.Request(url=abs_url, callback=self.parse_summary, meta={'loader': loader})
            # break
        cur_page = response.meta['page']
        if  cur_page < self.END_PAGE:
            cur_page += 1
            next_page = response.meta['template'].replace(f'trang-{cur_page - 1}', f'trang-{cur_page}')
            yield scrapy.Request(url=next_page, callback=self.parse, meta={'template': next_page, 'page': cur_page})


    def parse_summary(self, response):
        loader = response.meta['loader']
        loader.selector = response


        loader.add_xpath('title', "//h1[@class='title-page detail' or @class='e-magazine__title' or @class='special-news__title']/text()")
        loader.add_xpath('summary', "//h2[contains(@class, 'e-magazine__sapo') or @class='singular-sapo']/text()")

        category = response.xpath("//ul[@class='dt-text-c808080 dt-text-base dt-leading-5 dt-p-0 dt-list-none']/li/a/text() | //div[@class='category-name']/a/text() | //div[@class='e-magazine__maincate']/h3/a/text() | //div[@class='special-news__breadcrumb']//a/text()").extract()
        category = [c.strip().replace('/', '') for c in category if c.strip()] 
        category = '/'.join(category)
        loader.add_value('category', category)

        paragraphs = response.xpath("//div[@class='singular-content' or contains(@class, 'e-magazine__body')]/p")
        text = []
        for p in paragraphs:
            content = p.xpath(".//text()").extract()
            content = [c.strip() for c in content if c.strip()]
            content = ' '.join(content).strip()
            if content:
                text.append(content)
        loader.add_value('text', text)

        time = response.xpath("//time[@class='author-time' or @class='author-info_right' or @class='e-magazine__meta-item']/@datetime").extract_first()
        if time is not None:
            time = time.split(' ')
            day = time[0].replace('-', '/')
            day = day.split('/')[2] + '/' + day.split('/')[1] + '/' + day.split('/')[0]
            hour = time[1]
            loader.add_value('time', f"{day} - {hour}")

        author = response.xpath("//div[@class='author-name']/a/@href | //a[@class='e-magazine__meta']/text()").extract_first()
        text = response.xpath("//div[@class='singular-content' or contains(@class, 'e-magazine__body')]/p/text()").extract_first()

        if author is None and text is None and time is None:
            author = response.xpath("//a[@class='e-magazine__meta']/text()").extract()
            author = ' - '.join(author)
            loader.add_value('author', author)

            paragraphs = response.xpath("//div[contains(@class, 'e-magazine__body')]/p")
            text = []
            for p in paragraphs:
                content = p.xpath(".//text()").extract()
                content = [c.strip() for c in content if c.strip()]
                content = ' '.join(content).strip()
                if content:
                    text.append(content)
            loader.add_value('text', text)

            loader.add_xpath('time', "//time[@class='e-magazine__meta-item']/text()")
            loader.add_xpath('category', "//div[@class='e-magazine__maincate']/h3/a/text()")
            loader.add_xpath('title', "//h1[@class='e-magazine__title']/text()")
        else:
            if author is not None:
                loader.add_value('author', 'https://dantri.com.vn' + author)
            else:
                loader.add_xpath('author', '//div[@class="singular-content"]/p/strong/text()')
        
        yield loader.load_item()
