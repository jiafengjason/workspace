from urllib import parse

import scrapy
from scrapy import Request

class NewsSpider(scrapy.Spider):
    name = "news"
    allowed_domains = ["news.cnblogs.com"]
    start_urls = ["http://news.cnblogs.com/"]

    def parse(self, response):
        nodes = response.css('#news_list .news_block')
        for node in nodes:
            image_url = node.xpath('.//div[@class="entry_summary"]/a/img/@src').extract_first("")
            #image_url = node.css('.entry_summary a img::attr(src)').extract_first("")
            post_url = node.xpath('.//h2/a/@href').extract_first("")
            #post_url = node.css('h2 a::attr(href)').extract_first("")
            print(parse.urljoin(response.url, post_url))
            #yield Request(url=parse.urljoin(response.url, post_url), meta={"image_url": image_url}, callback=self.parse_detail)
        next = response.xpath('//div[@class="pager"]/a[contains(text(), "Next >")]/@href').extract_first("")
        #yield Request(url=urljoin(response.url, next), callback=parse)

    def parse_detail(self, response):
        pass
