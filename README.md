# 京东电商商品信息数据抓取

程序使用scrapy框架进行异步抓取京东商品信息

- 抓取京东电商商品的展示图片和评论图片
- 商品类目
- 商品颜色
- 商品类目
- 商品颜色
- 商品名
- 商品详情
- 品牌
- 商品编号
- 商品毛重
- 商品产地
- 适合肤质
- 功效
- 国产/进口
- 类别
- 产品产地
- 适用人群
- 规格

### spider模块

```python
# -*- coding: utf-8 -*-
import os
import re
import json
import scrapy
import hashlib
from PIL import Image
from io import BytesIO
from ..items import JdTradeItem


class JdtradeSpider(scrapy.Spider):
    name = 'jdtrade'
    allowed_domains = ['jd.com']
    start_urls = ['https://dc.3.cn/category/get']

    def parse(self, response):
        data = response.body.decode('gbk', 'ignore')
        dic = json.loads(data)
        # for x in dic['data']:
        #     for y in x['s']:
        #         for t in y['s']:
        #             print('#######')
        #             for i in t['s']:
        #                 print(i['n'])
        """美妆"""
        for y in dic['data'][5]['s'][0]['s'][1]['s']:
            keyword = y['n'].split('|')[1].replace('/', '_')
            if 'html' in y['n']:
                keywordurl = 'https://' + y['n'].split('|')[0].replace('-', ',')
            else:
                keywordurl = 'https://list.jd.com/list.html?cat=' + y['n'].split('|')[0].replace('-', ',')
            yield scrapy.Request(url=keywordurl, callback=self.tradepage_num, meta={
                'keyword': keyword,
                'keywordurl': keywordurl
            })
            return

    def tradepage_num(self, response):
        keyword = response.meta['keyword']
        keywordurl = response.meta['keywordurl']
        num = response.xpath('//*[@id="J_bottomPage"]/span[2]/em[1]/b/text()').extract_first()
        # trade_urls = response.xpath('//*[@class="p-img"]/a/@href').extract()
        for page in range(1, int(num)):
            tradeurl = keywordurl + "&page=%s" % page
            yield scrapy.Request(url=tradeurl, callback=self.tradepages, meta={
                'keyword': keyword,
            })
            return

    def tradepages(self, response):
        keyfolder = response.meta['keyword']
        trade_urls = response.xpath('//*[@class="p-img"]/a/@href').extract()
        for trade_url in trade_urls:
            trade_url = 'https:' + trade_url
            yield scrapy.Request(url=trade_url, callback=self.tradepage, meta={
                'keyfolder': keyfolder,
                'trade_url': trade_url,
            })

    def tradepage(self, response):
        keyfolder = response.meta['keyfolder']
        trade_url = response.meta['trade_url']
        items = JdTradeItem()
        trade_id = trade_url.split('/')[-1].split('.')[0]
        trade_param = response.xpath('//*[@id="detail"]/div[2]/div[1]/div[1]/ul/li/text()').extract()
        trade_type = response.xpath('//*[@id="crumb-wrap"]/div/div[1]/div/a/text()').extract()
        trade_map_url = 'https:' + response.xpath('//*[@id="spec-list"]/ul/li[1]/img/@src').extract_first()
        trade_colors = response.xpath('//*[@id="choose-attr-1"]/div[2]/div/@data-value').extract()
        trade_colorimgs = response.xpath('//*[@id="choose-attr-1"]/div[2]/div/a/img/@src').extract()
        trade_color_ids = response.xpath('//*[@id="choose-attr-1"]/div[2]/div/@data-sku').extract()
        items['trade_id'] = trade_id
        items['keyfolder'] = keyfolder
        items['trade_param'] = trade_param
        items['trade_type'] = trade_type
        items['trade_map_url'] = trade_map_url
        items['trade_colors'] = trade_colors
        items['trade_color_ids'] = trade_color_ids
        try:
            trade_name = response.xpath('//div[@class="sku-name"]/text()').extract()
        except:
            return
        if not trade_name[0].strip():
            trade_name = trade_name[1].strip()
        else:
            trade_name = trade_name[0].strip()

        if len(set(trade_colors)) == 0 or len(set(trade_color_ids)) == 0 or len(set(trade_colorimgs)) == 0:
            if trade_map_url.startswith('http'):
                img_url = trade_map_url
            else:
                img_url = 'http:' + trade_map_url
            if '60x76' in img_url:
                img_url = re.sub(r'60x76', "800x1026", img_url)
            elif '40x40' in img_url:
                img_url = re.sub(r'40x40', "800x1026", img_url)

            elif '50x64' in img_url:
                img_url = re.sub(r'50x64', "800x1026", img_url)
            elif 'n5' in img_url:
                img_url = re.sub(r'n5', "n1", img_url)

            else:
                print(trade_url)
                return
            data = {
                'trade_id': trade_id,
                'keyfolder': keyfolder,
                'trade_param': trade_param,
                'trade_type': trade_type,
                'trade_name': trade_name,
            }
            yield scrapy.Request(url=img_url, callback=self.save_map, dont_filter=True, meta={
                'data': data
            })
        else:
            for trade_color_id, trade_color, trade_colorimglink in zip(trade_color_ids, trade_colors, trade_colorimgs):
                if trade_colorimglink.startswith('http'):
                    img_url = trade_colorimglink
                else:
                    img_url = 'http:' + trade_colorimglink
                if '60x76' in img_url:
                    img_url = re.sub(r'60x76', "800x1026", img_url)
                elif '40x40' in img_url:
                    img_url = re.sub(r'40x40', "800x1026", img_url)

                elif '50x64' in img_url:
                    img_url = re.sub(r'50x64', "800x1026", img_url)
                elif 'n5' in img_url:
                    img_url = re.sub(r'n5', "n1", img_url)
                else:
                    print(trade_url)
                    continue
                data = {
                    'trade_id': trade_id,
                    'keyfolder': keyfolder,
                    'trade_param': trade_param,
                    'trade_type': trade_type,
                    'trade_map_url': trade_map_url,
                    'trade_color': trade_color,
                    'trade_color_id': trade_color_id,
                    'trade_colorimglink': img_url,
                    'trade_name': trade_name,
                }
                yield scrapy.Request(url=img_url, callback=self.savimg, dont_filter=True, meta={
                    'data': data,
                })

    def save_map(self, response):
        trade_id = response.meta['data']['trade_id']
        keyfolder = response.meta['data']['keyfolder']
        trade_types = response.meta['data']['trade_type']
        trade_name = response.meta['data']['trade_name']
        trade_param = response.meta['data']['trade_param']
        img_md5 = hashlib.md5(response.body)
        img_name = img_md5.hexdigest()
        file_path = os.path.join('美妆', keyfolder, trade_id, )
        im = hashlib.md5()
        im.update(response.body)
        image_md5_name = im.hexdigest()
        try:
            image = Image.open(BytesIO(response.body))
        except Exception as e:
            return
        if image.format == 'GIF' or image.format == 'WEBP':
            return
        image_name = image_md5_name + '.' + image.format
        try:
            os.makedirs(os.path.join(file_path, trade_id))
        except:
            pass
        with open(os.path.join(file_path, trade_id, image_name) + '.jpg', 'wb', ) as fb:
            fb.write(response.body)
        with open(os.path.join(file_path, trade_id) + 'trade_param.txt', 'w', encoding='utf-8') as pic:
            pic.write(f'商品类目: ')
            for i in trade_types:
                pic.write(i + '>')
            pic.write('\n')
            pic.write(f'商品名: {trade_name}\n')
            pic.write(f'商品详情: \n')
            for param in trade_param:
                if '\n' in param:
                    pic.write(param.replace('\n', '') + '\n')
                else:
                    pic.write(param + '\n')

    def savimg(self, response):
        trade_id = response.meta['data']['trade_id']
        keyfolder = response.meta['data']['keyfolder']
        trade_map_url = response.meta['data']['trade_map_url']
        trade_param = response.meta['data']['trade_param']
        trade_types = response.meta['data']['trade_type']
        trade_color = response.meta['data']['trade_color']
        trade_color_id = response.meta['data']['trade_color_id']
        trade_name = response.meta['data']['trade_name']
        file_path = os.path.join('美妆', keyfolder, trade_id, trade_color_id)
        im = hashlib.md5()
        im.update(response.body)
        image_md5_name = im.hexdigest()
        try:
            image = Image.open(BytesIO(response.body))
        except Exception as e:
            return
        if image.format == 'GIF' or image.format == 'WEBP':
            return
        image_name = image_md5_name + '.' + image.format
        try:
            os.makedirs(file_path)
        except:
            pass
        with open(os.path.join(file_path, image_name), 'wb') as file:
            file.write(response.body)
        with open(os.path.join(file_path, 'trade_param.txt'), 'w', encoding='utf-8') as pic:
            pic.write(f'商品类目: ')
            for i in trade_types:
                pic.write(i + '>')
            pic.write('\n')
            pic.write(f'商品颜色: {trade_color}\n')
            pic.write(f'商品名: {trade_name}\n')
            pic.write(f'商品详情: \n')
            for param in trade_param:
                if '\n' in param:
                    pic.write(param.replace('\n', '') + '\n')
                else:
                    pic.write(param + '\n')
```

