import scrapy
import pymongo
import re
from ..loaders import HhruLoader

db_url = 'mongodb://localhost:27017'
client = pymongo.MongoClient(db_url)
db = client['gu_data_mining_lesson_4']
db.drop_collection(db['autoyoula_v2'])
collection = db['autoyoula_v2']


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']

    _xpath_data_query = {
        "title": '//div[@data-target="advert-title"]/text()',
        "price": '//div[@data-target="advert-price"]/text()',
        "photos": '//div[contains(@class, "PhotoGallery_photoWrapper")]/figure//img/@src',
        "characteristics": "//div[contains(@class, 'AdvertCard_specs')]"
                           "//div[contains(@class, 'AdvertSpecs_row')]",
        "descriptions": '//div[@data-target="advert-info-descriptionFull"]/text()',
        "author": "//body/script[contains(text(), 'window.transitState = decodeURIComponent')]"
                  "/text()",
    }

    _xpaths_selectors = {
        "pagination": "//div[@data-qa='pager-block']//a[@class, 'bloko-button']/@href",
        #   "pagination": "//div[contains(@class, 'Paginator_block')]",
        #  "/a[@data-target-id='button-link-serp-paginator']/@href",
        "car": "//article[@data-target='serp-snippet']//a[@data-target='serp-snippet-title']/@href",
    }
#todo:
#response.xpath("//span[@class='pager-item-not-in-short-range']//a[. > 5]/text()").extract_first()
#'40'


    def _get_follow_xpath(self, response, selector, callback, **kwargs):
        for link in response.xpath(selector):
            yield response.follow(link, callback=callback, cb_kwargs=kwargs)

    def parse(self, response, *args, **kwargs):
        yield from self._get_follow_xpath(
            response, self._xpaths_selectors["pagination"], self.brand_parse
        )

    def brand_parse(self, response, **kwargs):
        yield from self._get_follow_xpath(
            response, self._xpaths_selectors["pagination"], self.brand_parse,
        )

    #     yield from self._get_follow_xpath(
    #         response, self._xpaths_selectors["car"], self.car_parse,
    #     )

    def car_parse(self, response):
        loader = HhruLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in self._xpath_data_query.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()
