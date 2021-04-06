import requests
from urllib.parse import urljoin
import bs4
from db import db
import typing
from datetime import datetime
import json

comments_api = 'https://gb.ru/api/v2/comments'


class GBPostParser:
    def __init__(self, init_url, database: db.Database):
        self.db = database
        self.init_url = init_url
        self.done_urls = set()
        self.tasks = []

    def get_task(self, url: str, callback: typing.Callable) -> typing.Callable:
        def task():
            soup = self._get_soup(url)
            return callback(url, soup)
        return task

    def run(self):
        task = self.get_task(self.init_url, self.parse_feed)
        self.tasks.append(task)
        self.done_urls.add(self.init_url)
        for task in self.tasks:
            task_result = task()
            if task_result:
                self.save(task_result)

    def save(self, data):
        self.db.create_post(data)

    def save_comment(self, data):
        self.db.create_comment(data)

    def _parse_comments(self, api_url, soup):
        comments_id = int(soup.find('comments').get('commentable-id'))
        _params = {
            'commentable_type': 'Post',
            'commentable_id': comments_id #2577
        }
        response = requests.get(api_url, _params)
        resp_json = response.json()
        _comment = {}
        for comment in resp_json:
            if comment:
               # print(comment)
                _comment_body = comment['comment']['body']
                _comment_writer = comment['comment']['user']['full_name']
                self.save_comment({'api_id': comments_id, 'comment_body': _comment_body, 'comment_writer': _comment_writer})
    #    return response

    def parse_post(self, url, soup):
        writer_data = soup.find('div', attrs={'itemprop': 'author'})
        str_date = soup.find('div', attrs={'class': 'blogpost-date-views'}).find('time').get('datetime').split('T')[0]
        try:
            img = soup.find('div', attrs={'itemprop': 'articleBody'}).find('img').get('src')
        except AttributeError:
            img = None

        data = {
            'post_data': {
                'title': soup.find('h1', attrs={'class': 'blogpost-title'}).text,
                'url': url,
                'image': img,
                'pub_date': datetime.strptime(str_date, '%Y-%m-%d'),
            },
            'writer_data': {
                'url': urljoin(url, writer_data.parent.attrs.get('href')),
                'name': writer_data.text
            },
            'tags_data': [{'url': urljoin(url, tag_a.attrs.get('href')), 'name': tag_a.text}
                          for tag_a in soup.find_all('a', attrs={'class': 'small'})],
         #   'comments_data': self.parse_comments(comments_api, comments_id)
        }
        self._parse_comments(comments_api, soup)
        return data

    def parse_feed(self, url, soup):
        ul_pagination = soup.find('ul', attrs={'class': 'gb__pagination'})
        pagination_urls = set(urljoin(url, url_a.attrs.get('href')) for url_a in ul_pagination.find_all('a') if url_a.attrs.get('href'))
        for page_url in pagination_urls:
            if page_url not in self.done_urls:
                task = self.get_task(page_url, self.parse_feed)
                self.done_urls.add(page_url)
                self.tasks.append(task)
        posts_urls = set(urljoin(url, url_p.attrs.get('href')) for url_p in soup.find_all('a', attrs={'class': 'post-item__title'}) if url_p.attrs.get('href'))
        for post_url in posts_urls:
            if post_url not in self.done_urls:
                task = self.get_task(post_url, self.parse_post)
                self.done_urls.add(post_url)
                self.tasks.append(task)

    def _get_response(self, url) -> requests.Response:
        response = requests.get(url)
        return response

    def _get_soup(self, url) -> bs4.BeautifulSoup:
        soup = bs4.BeautifulSoup(self._get_response(url).text, 'lxml')
        return soup


if __name__ == '__main__':
    database = db.Database('sqlite:///db_lesson_3.db')
    parser = GBPostParser('https://geekbrains.ru/posts', database)
    parser.run()
