import json
import requests
from pathlib import Path
import time

main_url = 'https://5ka.ru/api/v2/special_offers'
url_categories = 'https://5ka.ru/api/v2/categories'
Path(__file__).parent.joinpath('data').mkdir(exist_ok=True)
Path(__file__).parent.joinpath('data').joinpath('no_offers').mkdir(exist_ok=True)

def get_category_urls(url):
    response = requests.get(url)
    if response.status_code == 200:
        _json_data = response.json()
        parent_group_codes_list = [item['parent_group_code'] for item in _json_data]
        urls_with_categories = list(map(lambda s: f'{url_categories}/' + s, parent_group_codes_list))
    return urls_with_categories


def get_products_list_by_category(base_url, category):
    _page_no = 1
    products = []
    while True:
        url_params = {
            'store': None,
            'records_per_page': 12,
            'page': _page_no,
            'categories': category,
            'ordering': None,
            'price_promo__gte': None,
            'price_promo__lte': None,
            'search': None
        }
        _response = requests.get(main_url, params=url_params)
        if not _response.json().get('results', []):
            break
        elif _response.status_code == 200:
            products += _response.json().get('results', [])
            _page_no += 1
    return products


if __name__ == "__main__":
    urls = get_category_urls(url_categories)
    for link in urls:
        link_response = requests.get(link)
        if link_response.status_code == 200:
            json_data = link_response.json()
            for item in json_data:
                if item:
                    _dict = {'name': item['group_name'], 'code': item['group_code'], 'products': get_products_list_by_category(main_url, item['group_code'])}
                    print(_dict)
                    if _dict['products']:
                        Path(__file__).parent.joinpath('data').joinpath(f'{_dict["code"]}.json').write_text(json.dumps(_dict, indent=4, ensure_ascii=False))
                    else:
                        Path(__file__).parent.joinpath('data').joinpath('no_offers').joinpath(f'{_dict["code"]}.json').write_text(json.dumps(_dict, indent=4, ensure_ascii=False))
                    time.sleep(1)
