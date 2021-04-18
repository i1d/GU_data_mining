import scrapy
from ..loaders import AvitoLoader
#, HhruAuthorLoader


class AvitoSpiderSpider(scrapy.Spider):
    name = 'avito_spider'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/krasnodar/kvartiry/prodam']

# задача обойти пагинацию и подразделы квартир в продаже.
#
# Собрать данные:
# URL
# Title
# Цена
# Адрес (если доступен)
# Параметры квартиры (блок под фото)
# Ссылку на автора

    _xpath_data_query = {
        "title": '//h1[@data-qa="vacancy-title"]/text()',
        "salary": '//p[@class="vacancy-salary"]/span/text()',
        "description": '//div[@data-qa="vacancy-description"]//text()',
        "skills": '//div[@class="bloko-tag-list"]//div[contains(@data-qa, "skills-element")]/span[@data-qa="bloko-tag__text"]/text()',
        "author": '//a[@data-qa="vacancy-company-name"]/span/text()',
        "author_link": '//a[@data-qa="vacancy-company-name"]/@href',
    }

    _xpaths_selectors = {
        "pagination": "//div[@class='pagination-hidden-3jtv4']//a[@data-qa='pager-next']/@href",
        "flat": "//div[@class='iva-item-titleStep-2bjuh']//a/@href",
        "author": "//div[@class='vacancy-company__details']//a[@data-qa='vacancy-company-name']/@href",
        "author_vacancies": "//div[@class='employer-sidebar-block']//a[@data-qa='employer-page__employer-vacancies-link']/@href",
    }

    _xpath_author_query = {
        "author": '//div[@class="company-header"]//span[@data-qa="company-header-title-name"]/text()',
        "website": '//div[@class="employer-sidebar"]//a[@data-qa="sidebar-company-site"]/@href',
        "activity_areas": '//div[@class="employer-sidebar-block"]//p/text()',
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
            response, self._xpaths_selectors["flat"], self.flat_parse
        )

    def flat_parse(self, response):
        loader = AvitoLoader(response=response)
        loader.add_value("url", response.url)
        for key, xpath in self._xpath_data_query.items():
            loader.add_xpath(key, xpath)
        yield loader.load_item()
        # yield from self._get_follow_xpath(
        #     response, self._xpaths_selectors["author"], self.author_parse
        # )

    # def author_parse(self, response):
    #     author_loader = HhruAuthorLoader(response=response)
    #     author_loader.add_value("url", response.url)
    #     for key, xpath in self._xpath_author_query.items():
    #         author_loader.add_xpath(key, xpath)
    #     yield author_loader.load_item()
    #     yield from self._get_follow_xpath(
    #         response, self._xpaths_selectors["author_vacancies"], self.parse
    #     )
