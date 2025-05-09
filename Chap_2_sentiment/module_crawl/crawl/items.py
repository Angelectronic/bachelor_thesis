# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose

class ArticleItem(scrapy.Item):
    source = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip))
    url = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip))
    title = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip))
    time = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip))
    author = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip))
    category = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip))
    origin = scrapy.Field(output_processor=TakeFirst(), input_processor=MapCompose(str.strip))
    summary = scrapy.Field(output_processor=' '.join, input_processor=MapCompose(str.strip))
    text = scrapy.Field(input_processor=MapCompose(str.strip), output_processor='\n'.join)
