# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class XpcItem(scrapy.Item):
    # define the fields for your item here like:
    src = scrapy.Field()
    img = scrapy.Field()
    cate = scrapy.Field()
    lei = scrapy.Field()
    pub_time = scrapy.Field()
    bofang_count = scrapy.Field()
    zan = scrapy.Field()
    desc = scrapy.Field()
    tag = scrapy.Field()
    creator = scrapy.Field()
    title = scrapy.Field()
    video_url = scrapy.Field()
    video_profile = scrapy.Field()

