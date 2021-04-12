import scrapy
import pymongo
import re

db_url = 'mongodb://localhost:27017'
client = pymongo.MongoClient(db_url)
db = client['gu_data_mining_lesson_4']
db.drop_collection(db['autoyoula_v2'])
collection = db['autoyoula_v2']

class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']





    def _get_follow(self, response, select_str, callback, **kwargs):
        for a in response.css(select_str):
            url = a.attrib.get('href')
            yield response.follow(url, callback=callback, **kwargs)

    def parse(self, response):
        yield from self._get_follow(
            response,
            'div.TransportMainFilters_brandsList__2tIkv a.blackLink',
            self.brand_parse
        )

    def brand_parse(self, response):
        yield from self._get_follow(
            response,
            'div.Paginator_block__2XAPy a.Paginator_button__u1e7D',
            self.brand_parse
        )
        yield from self._get_follow(
            response,
            'article.SerpSnippet_snippet__3O1t2 a.SerpSnippet_name__3F7Yu',
            self.car_parse
        )

    def _get_specs(self, response):
        d = {}
        for div in response.css('div.AdvertSpecs_row__ljPcX'):
            d[div.css('.AdvertSpecs_label__2JHnS::text').extract_first()] = \
                div.css('.AdvertSpecs_data__xK2Qx::text').extract_first() \
                or div.css('.AdvertSpecs_data__xK2Qx a::text').extract_first()
        return d

    def _get_author_id(self, response):
        marker = "window.transitState = decodeURIComponent"
        for script in response.css("script"):
            try:
                if marker in script.css("::text").extract_first():
                    re_pattern = re.compile(r"youlaId%22%2C%22([a-zA-Z|\d]+)%22%2C%22avatar")
                    result = re.findall(re_pattern, script.css("::text").extract_first())
                    return (
                        response.urljoin(f"/user/{result[0]}").replace("auto.", "", 1)
                        if result
                        else None
                    )
            except TypeError:
                pass

    def car_parse(self, response):
        data = {
            'url': response.url,
            'title': response.css('div.AdvertCard_advertTitle__1S1Ak::text').extract_first(),
            'price': float(response.css('div.AdvertCard_price__3dDCr::text').extract_first().replace('\u2009', '')),
            'specs': self._get_specs(response),
            'description': response.css('div.AdvertCard_descriptionInner__KnuRi::text').extract_first(),
            'images': [img.attrib.get("src") for img in response.css("figure.PhotoGallery_photo__36e_r img")],
            'author': self._get_author_id(response),
        }
        collection.insert_one(data)
       # yield data
