import scrapy
from instagram_parse.loaders import InstagramLoader
import json
from datetime import datetime


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com', 'i.instagram.com']
    start_urls = ['https://www.instagram.com/']
    _login_url = 'https://www.instagram.com/accounts/login/ajax/'
    _tag_path = '/explore/tags/'
    _api_url = 'https://i.instagram.com/api/v1/tags/'

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

    def js_data_extract(self, response):
        script = response.xpath('//body/script[contains(text(), "window._sharedData")]/text()').extract_first()
        return json.loads(script[script.index("{"):-1])

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
               #     yield response.follow(f'{self._tag_path}{tag}/', callback=self.tag_parse)  #todo: починить
                    yield response.follow(f'{self._tag_path}{tag}/', callback=self.post_parse)
                 #   yield response.follow(f'{self._api_url}{tag}/sections/', callback=self.post_parse)
        else:
            yield self.auth(response)

    def tag_parse(self, response):
        js_data = self.js_data_extract(response)
        tag_data = js_data['entry_data']['TagPage'][0]['data']
        loader = InstagramLoader(response=response)
        loader.add_value("date_parse", datetime.now().strftime('%d.%m.%Y_%H:%M:%S'))
        loader.add_value("data", tag_data)
        yield loader.load_item()
     #   yield self.post_parse
     #   yield response.follow(f'{self._api_url}{self.tag}/sections/', callback=self.post_parse)

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
