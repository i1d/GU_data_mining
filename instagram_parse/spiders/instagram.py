import scrapy
from instagram_parse.loaders import InstagramLoader, InstagramUserLoader
import json
from datetime import datetime
from urllib.parse import urlencode, urlsplit, parse_qs
from instagram_parse.items import InstagramParseItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com', 'i.instagram.com']
    start_urls = ['https://www.instagram.com/']
    _login_url = 'https://www.instagram.com/accounts/login/ajax/'
    _tag_path = '/explore/tags/'
    _api_url = 'https://i.instagram.com/api/v1/tags/'
    _graphql = '/graphql/query/'
    _api_user_url = 'https://i.instagram.com/api/v1/users/'  
    # нужно найти pk  по имени пользователя

    def __init__(self, username, enc_password, tags, *args, **kwargs):
        super(InstagramSpider, self).__init__(*args, **kwargs)
        self.username = username
        self.enc_password = enc_password
        self.tags = tags

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

    def get_user_data(self, response):
        url = response.url
        q = urlsplit(url).query
        user_id = json.loads(parse_qs(q)['variables'][0])['id']

        js_data = response.json()
        user_follow = []

        next_page = js_data['data']['user']['edge_follow']['page_info']['has_next_page']
        end_cursor = js_data['data']['user']['edge_follow']['page_info']['end_cursor']
        edges = js_data['data']['user']['edge_follow']['edges']
        loader = InstagramUserLoader(response=response)
        loader.add_value("user", user_id)
        for edge in edges:
            user_follow.append(edge['node']['username'])
        loader.add_value("following", user_follow)
        if next_page:
            variables = {
                "id": user_id,
                "include_reel": False,
                "fetch_mutual": True,
                "first": 200,
                "after": end_cursor,
            }
            query = {"query_hash": '3dec7e2c57367ef3da3d987d89f9dbc8', "variables": json.dumps(variables)}
            yield response.follow(f"{self._graphql}?{urlencode(query)}", callback=self.get_user_data)
        else:
            pass
        yield loader.load_item()
        print('get_user_data')
        # return {'next_page': next_page, 'end_cursor': end_cursor, 'user_follow': user_follow}

    #   yield self.user_parse

    def parse(self, response):
        if b"json" in response.headers['Content-Type']:
            if response.json().get('authenticated'):
                for user in self.users:
                    yield response.follow(f'{self.start_urls[0]}{user}', callback=self.user_parse)
        else:
            yield self.auth(response)

    def user_parse(self, response):

        print('user_parse_start')
        js_data = self.js_data_extract(response)
        user_id = js_data['entry_data']['ProfilePage'][0]['graphql']['user']['id']
        user_name = js_data['entry_data']['ProfilePage'][0]['graphql']['user']['username']
        print(f'parsing: {user_name}; {user_id}...')

        # loader.add_value("user", user_id)
        variables = {
            "id": user_id,
            "include_reel": False,
            "fetch_mutual": True,
            "first": 200,
        }
        query = {"query_hash": '3dec7e2c57367ef3da3d987d89f9dbc8', "variables": json.dumps(variables)}

        yield response.follow(f"{self._graphql}?{urlencode(query)}", callback=self.get_user_data)
        #
        # loader = InstagramUserLoader(response=response)
        # loader.add_value("user", user_id)
        # loader.add_value("followers", followers)
        # yield loader.load_item()
        print('user_parse_end')
