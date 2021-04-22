# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
import pymongo
from itemadapter import ItemAdapter
from scrapy.exporters import JsonItemExporter


class InstagramParsePipeline:
    def process_item(self, item, spider):
        return item


class JsonExporterPipeline(object):
    def __init__(self):
        self.file = open('instagram_users.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class InstagramParseMongoPipeline:
    def __init__(self):
        client = pymongo.MongoClient()
        self.db = client["instagram_users_parse"]

    def process_item(self, item, spider):
        self.db[spider.name].insert_one(item)
        return item


class InstagramImageDownloadPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        # yield Request(item.get('data', []).get('image_versions2', []).get('candidates', [])[0].get('url', []))
        # yield Request(item['data']['image_versions2']['candidates'][0]['url'])
        try:
            img_url = item['data']['image_versions2']['candidates'][0]['url']
            yield Request(img_url)
        except KeyError:
            for media in item['data']['carousel_media']:
                img_url = media['image_versions2']['candidates'][0]['url']
                yield Request(img_url)

    def item_completed(self, results, item, info):
        if 'data' in item:
            # item['data']['image_versions2']['candidates'][0]['url'] = [itm[1] for itm in results]
            item['data'] = [itm[1] for itm in results]
        return item
