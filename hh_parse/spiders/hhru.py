import scrapy
import pymongo
import re
from ..loaders import HhruLoader, HhruAuthorLoader
from urllib.parse import urljoin, urlparse

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
        "title": '//h1[@data-qa="vacancy-title"]/text()',
        "salary": '//p[@class="vacancy-salary"]/span/text()',
        "description": '//div[@data-qa="vacancy-description"]//text()',
        "skills": '//div[@class="bloko-tag-list"]//div[contains(@data-qa, "skills-element")]/span[@data-qa="bloko-tag__text"]/text()',
        "author": '//a[@data-qa="vacancy-company-name"]/span/text()',
        "author_link": '//a[@data-qa="vacancy-company-name"]/@href',
    }

    _xpaths_selectors = {
        "pagination": "//div[@data-qa='pager-block']//a[@data-qa='pager-next']/@href",
        "vacancy": "//div[@class='vacancy-serp-item__info']//a[@data-qa='vacancy-serp__vacancy-title']/@href",
        "author": "//div[@class='vacancy-company__details']//a[@data-qa='vacancy-company-name']/@href"
    }

    _xpath_author_query = {
        # 1. Название
        "author": '//div[@class="company-header"]//span[@data-qa="company-header-title-name"]/text()',
        # 2. сайт ссылка (если есть)
        "website": '//div[@class="employer-sidebar"]//a[@data-qa="sidebar-company-site"]/@href',
        # 3. сферы деятельности (списком)
        "activity_areas": '//div[@class="employer-sidebar-block"]//p/text()',
        # 4. Описание
        "description": '//div[@data-qa="company-description-text"]/text()',
    }

    def _get_follow_xpath(self, response, selector, callback):
        for link in response.xpath(selector):
            yield response.follow(link, callback=callback)

    def parse(self, response):
        yield from self._get_follow_xpath(
            response, self._xpaths_selectors["pagination"], self.parse
        )
        yield from self._get_follow_xpath(
            response, self._xpaths_selectors["vacancy"], self.vacancy_parse
        )

    def vacancy_parse(self, response):
        loader = HhruLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in self._xpath_data_query.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()
        yield from self._get_follow_xpath(
            response, self._xpaths_selectors["author"], self.author_parse
        )

    def author_parse(self, response):
        author_loader = HhruAuthorLoader(response=response)
        author_loader.add_value("url", response.url)
        for key, xpath in self._xpath_author_query.items():
            author_loader.add_xpath(key, xpath)
        yield author_loader.load_item()
