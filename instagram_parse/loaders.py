from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join


class InstagramLoader(ItemLoader):
    default_item_class = dict
    date_parse_out = TakeFirst()
    data_out = TakeFirst()


class InstagramUserLoader(ItemLoader):
    default_item_class = dict
    user_out = TakeFirst()
 #   following_out = Join()
    # date_parse_out = TakeFirst()
    # data_out = TakeFirst()
