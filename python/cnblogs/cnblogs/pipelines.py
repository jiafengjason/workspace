# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json

from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline

class JsonPipeline:
    def open_spider(self, spider):
        self.file = open("items.json", "w")

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        return item

class ImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "image_url" in item:
            for ok, value in results:
                image_path = value["path"]
            item["image_path"] = image_path
        return item

class CnblogsPipeline:
    def process_item(self, item, spider):
        return item
