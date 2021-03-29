import requests
from urllib.parse import urljoin
import bs4
from datetime import datetime
import pymongo

main_url = 'https://magnit.ru/promo/?geo=moskva'
db_url = 'mongodb://localhost:27017'
months = {
    'января': 1,
    'февраля': 2,
    'марта': 3,
    'апреля': 4,
    'мая': 5,
    'июня': 6,
    'июля': 7,
    'августа': 8,
    'сентября': 9,
    'октября': 10,
    'ноября': 11,
    'декабря': 12
}

response = requests.get(main_url)
client = pymongo.MongoClient(db_url)
db = client['gu_data_mining']
db.drop_collection(db['lesson_2'])
collection = db['lesson_2']

if response.status_code == 200:
    soup = bs4.BeautifulSoup(response.text, features='lxml')
    a_list = soup.find_all('a', attrs='card-sale')
    for a_list_item in a_list:
        url = urljoin(main_url, a_list_item.get('href'))
        try:
            promo_name = a_list_item.find('div', attrs='card-sale__header').text
        except AttributeError:
            promo_name = None
        try:
            product_name = a_list_item.find('div', attrs='card-sale__title').text
        except AttributeError:
            product_name = None
        try:
            _old_price_integer = int(a_list_item.find('div', attrs='label__price_old').find('span', attrs='label__price-integer').text)
            _old_price_decimal = int(a_list_item.find('div', attrs='label__price_old').find('span', attrs='label__price-decimal').text)
            old_price = _old_price_integer + _old_price_decimal / 100
        except (AttributeError, ValueError):
            old_price = None
        try:
            _new_price_integer = int(a_list_item.find('div', attrs='label__price_new').find('span', attrs='label__price-integer').text)
            _new_price_decimal = int(a_list_item.find('div', attrs='label__price_new').find('span', attrs='label__price-decimal').text)
            new_price = _new_price_integer + _new_price_decimal / 100
        except (AttributeError, ValueError):
            new_price = None
        image_url = urljoin(main_url, a_list_item.find('img').get('data-src'))
        try:
            _dates_list = a_list_item.find('div', attrs='card-sale__date').text.strip().split('\n')
            for _date in _dates_list:
                if _date[0] == 'с':
                    _str_dt_list = _date.split()
                    _str_dt = f'{_str_dt_list[1]}.{months[_str_dt_list[2]]}.2021'
                    date_from = datetime.strptime(_str_dt, '%d.%m.%Y')
                elif _date[0:2] == 'до':
                    _str_dt_list = _date.split()
                    _str_dt = f'{_str_dt_list[1]}.{months[_str_dt_list[2]]}.2021'
                    date_to = datetime.strptime(_str_dt, '%d.%m.%Y')
        except AttributeError:
            date_from = None
            date_to = None
        collection.insert_one({
            'url': url,
            'promo_name': promo_name,
            'product_name': product_name,
            'old_price': old_price,
            'new_price': new_price,
            'image_url': image_url,
            'date_from': date_from,
            'date_to': date_to
        })
