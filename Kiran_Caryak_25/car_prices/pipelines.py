# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class CarPricesPipeline:
    def process_item(self, item, _):
        return item


class MongoPipeline:
    def __init__(self):
        pass

    def open_spider(self, _):
        pass

    def close_spider(self, _):
        pass

    def process_item(self, item, spider):
        item_dict = ItemAdapter(item).asdict()

        spider.final_result = item_dict

        if spider.database is not None:
            spider.database.handle[spider.collection_name].insert_one(item_dict)

        return item
