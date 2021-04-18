import re
from scrapy.loader import ItemLoader
from scrapy import Selector
from itemloaders.processors import TakeFirst, MapCompose, Join


# def clear_salary(salary: str) -> str:
#     try:
#         result = "".join(salary).replace("\xa0", "")
#     except ValueError:
#         result = None
#     return result
#
# def get_author_link(link):
#     author_link = f"https://hh.ru{link}"
#     return author_link


class AvitoLoader(ItemLoader):
    default_item_class = dict
    # url_out = TakeFirst()
    # title_out = TakeFirst()
    # # salary_in = MapCompose(clear_salary)
    # salary_out = Join()
    # description_out = Join()
    # author_out = Join()
    # # author_link_in = MapCompose(get_author_link)
    # author_link_out = TakeFirst()


# class HhruAuthorLoader(ItemLoader):
#     default_item_class = dict
#     url_out = TakeFirst()
#     author_out = Join()
#     website_out = TakeFirst()
