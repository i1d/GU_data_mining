# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstagramParseItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    user = scrapy.Field()
    following = scrapy.Field()
   # pass
