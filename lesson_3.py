import requests
from urllib.parse import urljoin
import bs4
from datetime import datetime
import pymongo
import typing


class GBPostParser:
    def __init__(self, init_url):
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
                pass

    def save(self):
        pass

    def parse_post(self, url, soup):
        pass

    def parse_feed(self, url, soup):
        pass

    def _get_response(self, url) -> requests.Response:
        #todo: обработать статус коды
        response = requests.get(url)
        return response

    def _get_soup(self, url) -> bs4.BeautifulSoup:
        soup = bs4.BeautifulSoup(self._get_response(url).text)
        return soup


if __name__ == '__main__':
    parser = GBPostParser('https://geekbrains.ru/posts')
    parser.run()
