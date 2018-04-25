# -*- coding: utf-8 -*-
import re
from bs4 import BeautifulSoup as bfs
from scrapy import Spider, Request
from taobao.items import TaobaoItem

class GoodsSpider(Spider):
    name = 'goods'
    # allowed_domains = ['www.taobao.com','www.baidu.com']
    search_url = 'http://www.taobao.com/'
    tb_search_url = 'https://s.taobao.com/list?cat={id}'
    page = 0
    keywords = ''
    batch = 60

    def start_requests(self):
        url = self.search_url
        yield Request(url, callback=self.parse_spm)

    def parse_spm(self, response):
        market_links = response.xpath('//ul[@class="service-bd"]//a/@href')
        market_names = response.xpath('//ul[@class="service-bd"]//a/text()').extract()
        for i, j in enumerate(market_links.extract()):
            if not j.startswith('https:'):
                j = 'https:' + j
            yield Request(j, callback=self.parse_spm_handle, meta={'data': market_names[i]})

    def parse_spm_handle(self, response):
        market_names = response.meta['data']

        if market_names == '女装':
            cloth_url = response.xpath('//*[@id="sm-nav-2014"]/div[2]/div[2]/div/div[2]//a/@href')
            ids = []
            for link in cloth_url.extract():
                if link:
                    id = re.search(r'.*?cat=(\d+).*?', link).group(1)
                    ids.append(id)
            for id in list(set(ids)):
                cat_link = self.tb_search_url.format(id=id)
                yield Request(cat_link, callback=self.parse_goods_handle, meta={'data': market_names})
        else:
            pass

    def parse_goods_handle(self, response):
        total_page = re.search(r'"totalPage":(\d+)', response.text)

        if not total_page:
            print(response.url)
            return

        total_page = total_page.group(1)

        for page in range(int(total_page)):
            next_page_url = response.url
            if 's=' in next_page_url:
                next_page_url = re.sub(r"s=\d+", 's=%s' % (page * self.batch), next_page_url, 1)
            else:
                next_page_url += '&s=%s' % (page * self.batch)
            yield Request(next_page_url, callback=self.parse_next_page)

    def parse_next_page(self, response):
        ret = re.findall(
            r'"sku":.*?"nid":"(\d+).*?"category":"(\d+).*?"title":"(.*?)".*?"pic_url":"(.*?)".*?"detail_url":"(.*?)".*?"view_price":"(.*?)".*?"view_fee":"(.*?)".*?"item_loc":"(.*?)".*?"view_sales":"(\d+).*?"comment_count":"(\d+).*?"user_id":"(\d+).*?"nick":"(.*?)"',
            response.text)
        item = TaobaoItem()
        if not ret:
            return None

        for detail in ret:

            if not detail[3].startswith('https:'):
                image_url = 'https:' + detail[3]
            else:
                image_url = detail[3]
            image_url=re.sub(r'\\u003d','=',image_url)
            image_url=re.sub(r'\\u0026','&',image_url)

            if not detail[4].startswith('https:'):
                detail_url = 'https:' + detail[4]
            else:
                detail_url = detail[4]
            detail_url=re.sub(r'\\u003d','=',detail_url)
            detail_url=re.sub(r'\\u0026','&',detail_url)

            product = {
                "id": detail[0],
                "category": detail[1],
                "title": detail[2],
                "image_url": image_url,
                "detail_url": detail_url,
                "price": detail[5],
                "post": detail[6],
                "city": detail[7],
                "deal": detail[8],
                "comment": detail[9],
                "boss_id": detail[10],
                "boss": detail[11],
            }
            for field in item.fields:
                if field in product.keys():
                    item[field] = product[field]
            yield item
