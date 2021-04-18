import scrapy


class AvitoSpiderSpider(scrapy.Spider):
    name = 'avito_spider'
    allowed_domains = ['avito.ru']
    start_urls = ['http://avito.ru/']

    def parse(self, response):
        pass
