from urllib import parse

import scrapy
from scrapy import Request
from scrapy.loader import ItemLoader

from cnblogs.items import CnblogsLoader
from cnblogs.items import CnblogsNewsItem

class NewsSpider(scrapy.Spider):
    name = "news"
    allowed_domains = ["news.cnblogs.com"]
    start_urls = ["http://news.cnblogs.com/"]

    def parse(self, response):
        nodes = response.css('#news_list .news_block')[1:2]
        for node in nodes:
            # image_url = [node.xpath('.//div[@class="entry_summary"]/a/img/@src').extract_first("")]
            # image_url = node.css('.entry_summary a img::attr(src)').extract_first("")
            # post_url = node.xpath('.//h2/a/@href').extract_first("")
            # post_url = node.css('h2 a::attr(href)').extract_first("")

            # item = CnblogsNewsItem()
            # item.url = node.xpath('.//h2/a/@href').extract_first("")
            # item.image = node.xpath('.//div[@class="entry_summary"]/a/img/@src').extract_first("")

            l = CnblogsLoader(item=CnblogsNewsItem(), selector=node, response=response)
            l.context["response"] = response
            l.add_xpath('title', './/h2/a/text()')
            l.add_xpath('url', './/h2/a/@href')
            l.add_xpath('image_url', './/div[@class="entry_summary"]/a/img/@src')
            item = l.load_item()

            yield item

            #yield Request(url=parse.urljoin(response.url, post_url), meta={"image_url": image_url}, callback=self.parse_detail)
        next = response.xpath('//div[@class="pager"]/a[contains(text(), "Next >")]/@href').extract_first("")
        #yield Request(url=urljoin(response.url, next), callback=parse)

    def parse_detail(self, response):
        pass
