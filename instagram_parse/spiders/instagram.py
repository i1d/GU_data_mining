import scrapy
from instagram_parse.loaders import InstagramLoader, InstagramUserLoader
import json
from datetime import datetime
from urllib.parse import urlencode, urlsplit, parse_qs


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com', 'i.instagram.com']
    start_urls = ['https://www.instagram.com/']
    _login_url = 'https://www.instagram.com/accounts/login/ajax/'
    _tag_path = '/explore/tags/'
    _api_url = 'https://i.instagram.com/api/v1/tags/'
    _graphql = '/graphql/query/'
    _api_user_url = 'https://i.instagram.com/api/v1/users/'  # 45240494484/info/ - получаем всю инфу о пользователе

    # 646913944 = tatlmd
    #
    # нужно найти pk  по имени пользователя

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

    def get_user_data(self, response, loader):
        yield from loader
        ############  loader = response.meta.get('loader')
        url = response.url
        q = urlsplit(url).query
        user_id = json.loads(parse_qs(q)['variables'][0])['id']
        js_data = response.json()
        #    user_follow = []
        next_page = js_data['data']['user']['edge_follow']['page_info']['has_next_page']
        end_cursor = js_data['data']['user']['edge_follow']['page_info']['end_cursor']
        edges = js_data['data']['user']['edge_follow']['edges']
        # loader = InstagramUserLoader(response=response)
        # loader.add_value("user", user_id)
        for edge in edges:
            #       user_follow.append(edge['node']['username'])
            loader.add_value("following", edge['node']['username'])
        yield loader
        if next_page:
            variables = {
                "id": user_id,
                "include_reel": False,
                "fetch_mutual": True,
                "first": 200,
                "after": end_cursor,
            }
            query = {"query_hash": '3dec7e2c57367ef3da3d987d89f9dbc8', "variables": json.dumps(variables)}
            yield response.follow(f"{self._graphql}?{urlencode(query)}", callback=self.get_user_data,
                                  cb_kwargs=dict(loader))
        else:
            pass
        print('get_user_data')

    #   yield self.user_parse

    def parse(self, response):
        if b"json" in response.headers['Content-Type']:
            if response.json().get('authenticated'):
                for user in self.users:
                    #     yield response.follow(f'{self._tag_path}{tag}/', callback=self.tag_parse)  #todo: починить
                    #   yield response.follow(f'{self._tag_path}{tag}/', callback=self.post_parse)
                    yield response.follow(f'{self.start_urls[0]}{user}', callback=self.user_parse)
                #   yield response.follow(f'{self._api_url}{tag}/sections/', callback=self.post_parse)
        else:
            yield self.auth(response)

    def user_parse(self, response):
        js_data = self.js_data_extract(response)
        user_id = js_data['entry_data']['ProfilePage'][0]['graphql']['user']['id']
        user_name = js_data['entry_data']['ProfilePage'][0]['graphql']['user']['username']
        print(f'parsing: {user_name}; {user_id}...')
        loader = InstagramUserLoader(response=response)
        loader.add_value("user", user_id)
        # yield response.follow(f'https://i.instagram.com/api/v1/users/32412777121/info/') #test
        # a = self.get_user_data(response)
        #  https://www.instagram.com/graphql/query/?query_hash=3dec7e2c57367ef3da3d987d89f9dbc8&variables={%22id%22:%22910971613%22,%22include_reel%22:false,%22fetch_mutual%22:true,%22first%22:200,%22after%22:%22QVFDWHBBRS1HZTI5TFBVQldndUh6eHFwdElNOVFTM1hkUlV6cUpid0ppdXhSdVJQWGNMVm1Bd3BDUENMbHFQZ0lOekprRll3UU0xV3RJeGNiV1dSV0FFZg==%22}
        variables = {
            "id": user_id,
            "include_reel": False,
            "fetch_mutual": True,
            "first": 200,
            #  "after": "QVFDWHBBRS1HZTI5TFBVQldndUh6eHFwdElNOVFTM1hkUlV6cUpid0ppdXhSdVJQWGNMVm1Bd3BDUENMbHFQZ0lOekprRll3UU0xV3RJeGNiV1dSV0FFZg==",
        }
        query = {"query_hash": '3dec7e2c57367ef3da3d987d89f9dbc8', "variables": json.dumps(variables)}
        yield response.follow(f"{self._graphql}?{urlencode(query)}", callback=self.get_user_data,
                              cb_kwargs=dict(loader))
        yield loader.load_item()
        print('user_parse')

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
