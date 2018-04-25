# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class TaobaoItem(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    id = Field()            # 商品ID
    category = Field()      # 类别ID
    image_url = Field()     # 默认图片地址
    detail_url = Field()    # 详情页地址
    title = Field()         # 标题
    price = Field()         # 价格
    deal = Field()          # 成交量
    comment = Field()       # 评论数
    shop = Field()          # 店铺名
    post = Field()          # 邮费
    city = Field()          # 所在地
    boss_id = Field()       # 展柜ID
    boss = Field()          # 展柜名字
