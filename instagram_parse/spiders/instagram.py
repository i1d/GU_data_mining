import scrapy
from instagram_parse.loaders import InstagramLoader
import json
from datetime import datetime


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    _login_url = 'https://www.instagram.com/accounts/login/ajax/'
    _tag_path = '/explore/tags/'

    def __init__(self, username, enc_password, tags, *args, **kwargs):
        super(InstagramSpider, self).__init__(*args, **kwargs)
        self.username = username
        self.enc_password = enc_password
        self.tags = tags

    # Задача авторизованным пользователем обойти список произвольных тегов,
    # Сохранить структуру Item олицетворяющую сам Tag (только информация о теге)
    # Сохранить структуру данных поста, Включая обход пагинации. (каждый пост как отдельный item, словарь внутри node)
    # Все структуры должны иметь след вид
    # date_parse (datetime) время когда произошло создание структуры
    # data - данные полученые от инстаграм
    # Скачать изображения всех постов и сохранить на диск

    _xpath_data_query = {
        "title": '//div[@class="title-info-main"]/span/text()',
        "price": '//div[@class="item-price-wrapper"]//span[@class="js-item-price"]/@content',
        "address": '//div[@class="item-address"]//span[@class="item-address__string"]/text()',
        "parameters": '//div[@class="item-params"]/text()',
        "author_link": '//div[@class="seller-info-value"]//a/@href',
    }

    _xpaths_selectors = {
        "pagination": "//div[@class='pagination-hidden-3jtv4']//a/@href",
        "flat": "//div[@class='iva-item-titleStep-2bjuh']//a/@href",
    }



    def js_data_extract(self, response):
        script = response.xpath('//body/script[contains(text(), "window._sharedData")]/text()').extract_first()
        return json.loads(script[script.index("{"):-1])

    def _get_follow_xpath(self, response, selector, callback):
        for link in response.xpath(selector):
            yield response.follow(link, callback=callback)

    def auth(self, response):
        js_data = self.js_data_extract(response)
        return scrapy.FormRequest(
            self._login_url,
            method="POST",
            callback=self.parse,
            formdata={
                'username': self.username,
                'enc_password': self.enc_password
            },
            headers={'X-CSRFToken': js_data['config']['csrf_token']}
        )

    def parse(self, response):
        if b"json" in response.headers['Content-Type']:
            if response.json().get('authenticated'):
                for tag in self.tags:
                    yield response.follow(f'{self._tag_path}{tag}/', callback=self.post_parse)
        else:
            yield self.auth(response)

    def tag_parse(self, response):
        js_data = self.js_data_extract(response)
        print(1)
        # section = js_data['entry_data']['TagPage'][0]['data']['top']['sections']


        # js_object = js_data['sections'][]
    def post_parse(self, response):
        js_data = self.js_data_extract(response)

        sections = js_data['entry_data']['TagPage'][0]['data']['top']['sections']  # list
        for section in sections:
            medias = section['layout_content']['medias']  # list
            for media in medias:
                data = media['media']
                loader = InstagramLoader(response=response)
                loader.add_value("date_parse", datetime.now().strftime('%d.%m.%Y_%H:%M:%S'))
                loader.add_value("data", data)
                yield loader.load_item()


    # def flat_parse(self, response):
    #     loader = InstagramLoader(response=response)
    #     loader.add_value("url", response.url)
    #     for key, xpath in self._xpath_data_query.items():
    #         loader.add_xpath(key, xpath)
    #     yield loader.load_item()
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
