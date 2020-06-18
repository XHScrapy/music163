# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Music163Item(scrapy.Item):
    # art_name = scrapy.Field()
    # album_name = scrapy.Field()
    # music_name = scrapy.Field()
    music_id = scrapy.Field()
    file_name = scrapy.Field()
