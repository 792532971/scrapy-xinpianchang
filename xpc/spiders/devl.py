# -*- coding: utf-8 -*-
import scrapy
from scrapy.utils.project import get_project_settings
from xpc.items import XpcItem
import re
import json


class DevlSpider(scrapy.Spider):
    count = 0
    name = 'devl'
    allowed_domains = ['xinpianchang.com']
    start_urls = ['https://www.xinpianchang.com/channel/index/sort-like?from=tabArticle']

    def parse(self, response):
        lists = response.xpath("//ul[@class='video-list']/li/@data-articleid").extract()
        url = 'https://www.xinpianchang.com/a%s?from=ArticleList'
        for pid in lists:
            # yield response.follow(url % pid, callback=self.parse_detail)
            self.count += 1
            yield scrapy.Request(url % pid, meta={"pid": pid}, callback=self.parse_detail)
        next_url = response.xpath("//a[@title='下一页']/@href").get()
        if next_url:
            print("下一页+++____________________________________________________________")
            yield scrapy.Request(response.urljoin(next_url), callback=self.parse)

    def parse_detail(self, response):
        pid = response.meta['pid']
        item = XpcItem()
        item['src'] = response.url
        item['img'] = re.findall(r"https://cs.xinpianchang.com/uploadfile/article/\d{4}/\d{2}/\d{2}/\w+.jpeg@960w_540h_1e_1c.jpg", response.text)[0]
        item['pub_time'] = response.xpath("//span[@class='update-time v-center']/i/text()").get()
        cate = ''.join(response.xpath("//div[@class='filmplay-intro fs_12 fw_300 c_b_9']/span[1]//text()").getall())
        item['cate'] = re.sub(r'\n|\t|\r', '', cate)
        if response.xpath("//span[@style='margin-right: 5px;']//text()").getall():
            lei = ''.join(response.xpath("//span[@style='margin-right: 5px;']//text()").getall())
            item['lei'] = re.sub(r'\n|\t|\r', '', lei)
        else:
            item['lei'] = ''
        item['bofang_count'] = response.xpath("//div[@title='站内播放数']/i/text()").get()
        item['zan'] = response.xpath("//span[@class='v-center like-counts fs_12 c_w_f fw_300']/text()").get()
        item['desc'] = ''.join(response.xpath("//div[@class='filmplay-info-desc left-section']/p//text()").extract())
        tt = response.xpath("//div[@class='fs_12 fw_300 c_b_3 tag-wrapper']//text()").getall()
        t1 = ",".join(self.evens(tt))
        item['tag'] = re.sub(r'\n|\t|\r', '', t1)
        c = response.xpath("//ul[@class='creator-list']/li/div[2]/@data-username").getall()
        item['creator'] = ','.join(c)
        # 写到后面才发现这个接口,   就这样吧
        # 直接请求这个接口数据就出来了 不用这么麻烦 这么多xpath  暂时就这样吧
        yield scrapy.Request('https://app.xinpianchang.com/article/%s?expand=user_status' % pid, meta={"item": item}, callback=self.parse_video)

    def parse_video(self, response):
        item = response.meta['item']
        data = json.loads(response.text)['data']
        item['title'] = data['title']
        video_info = data['video']['content']['progressive'][0]
        item['video_url'] = video_info['url']
        item['video_profile'] = video_info['profile']
        print('正在爬取%s' % item['title'])
        print(self.count)
        print('***' * 10)
        yield item

    @staticmethod
    def evens(l):
        return l[1::2]