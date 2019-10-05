# -*- coding: utf-8 -*-
import scrapy
from scrapy.utils.project import get_project_settings
from xpc.items import XpcItem
import re
import random
import string
import json

# 爬取到20页会有登录验证，所以需要获取cookies
# fiddler抓包获取cookies  每次请求携带cookie
cookies = dict(Authorization='707BECB32ED661AC72ED66467C2ED66AB8A2ED6621FF32F4B0E5')


def gen_sessionid():
    # 生成26位小写字母加数子组合可以重复
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=26))


class DevlSpider(scrapy.Spider):
    page_count = 1

    name = 'devl'
    allowed_domains = ['xinpianchang.com']
    start_urls = ['https://www.xinpianchang.com/channel/index/sort-like?from=tabArticle']

    def parse(self, response):
        self.page_count += 1
        if self.page_count >= 30:
            # 这个站是根据PHPSESSID反扒，每次请求PHPSESSID都是固定的 PHPSESSID 达到指定次数就会提示系统繁忙
            # 所以这里到达30页的时候就重新给它的PHPSESSID赋值 （26位小写字母加数字组合可以重复）
            # 测试时它的页面到达70页就会提示
            self.page_count = 0
            cookies.update(PHPSESSID=gen_sessionid())
        lists = response.xpath("//ul[@class='video-list']/li/@data-articleid").extract()
        url = 'https://www.xinpianchang.com/a%s?from=ArticleList'
        for pid in lists:
            yield scrapy.Request(url % pid, meta={"pid": pid})
        next_url = response.xpath("//a[@title='下一页']/@href").get()
        if next_url:
            yield scrapy.Request(response.urljoin(next_url), callback=self.parse, cookies=cookies)

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
        print(self.page_count)
        yield item

    @staticmethod
    def evens(l):
        # 取列表偶数
        return l[1::2]