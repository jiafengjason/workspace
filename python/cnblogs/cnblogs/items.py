# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from urllib.parse import urljoin

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import Identity, TakeFirst, MapCompose, Join

class CnblogsLoader(ItemLoader):
    default_output_processor = TakeFirst()

class CnblogsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

def parse_url(url, loader_context):
    response = loader_context.get("response", None)
    return urljoin(response.url, url)

def parse_image(image):
    if image.startswith("//"):
        return "https:"+image
    else:
        return image

class CnblogsNewsItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field(
        input_processor=MapCompose(parse_url)
    )
    image_url = scrapy.Field(
        input_processor=MapCompose(parse_image),
        output_processor=Identity()
    )
    image_path = scrapy.Field()
