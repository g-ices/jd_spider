# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JdTradeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    keyfolder = scrapy.Field()
    trade_id = scrapy.Field()
    trade_param = scrapy.Field()
    trade_type = scrapy.Field()
    trade_url = scrapy.Field()
    trade_map_url = scrapy.Field()
    trade_comment_url = scrapy.Field()
    trade_colors = scrapy.Field()
    trade_color_ids = scrapy.Field()


# li = ['\n                                ', ' \n                                韩国爱茉莉 兰芝(LANEIGE)  雪纱丝柔淡紫色隔离霜30ml SPF25/PA++（修饰泛黄 提亮肤色）            ']
# if not li[0].strip():
#     print(1)
# if li[1].strip():
#     print(2)


