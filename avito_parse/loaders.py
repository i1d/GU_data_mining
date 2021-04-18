import re
from scrapy.loader import ItemLoader
from scrapy import Selector
from itemloaders.processors import TakeFirst, MapCompose, Join


def clear_price(price: str) -> float:
    try:
        result = float(price)
    except ValueError:
        result = None
    return result
#
# def get_author_link(link):
#     author_link = f"https://hh.ru{link}"
#     return author_link


class AvitoLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    # title_out = TakeFirst()
    price_in = MapCompose(clear_price)
    price_out = TakeFirst()
    address_out = TakeFirst()
    # description_out = Join()
    author_link_out = TakeFirst()
    # # author_link_in = MapCompose(get_author_link)


# class HhruAuthorLoader(ItemLoader):
#     default_item_class = dict
#     url_out = TakeFirst()
#     author_out = Join()
#     website_out = TakeFirst()
