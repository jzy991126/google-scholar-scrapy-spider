# -*- coding: utf-8 -*-
import scrapy
from urllib.parse import urlencode
from urllib.parse import urlparse
import json
from datetime import datetime


def get_queries():
    with open('paper-list.txt') as f:
        lines = f.readlines()
    res = []
    for line in lines:
        res.append(line.strip())
    return res

API_KEY = '58de7fccdacf4aa72444020c1616e307'  #gitignore

def get_url(url):
    payload = {'api_key': API_KEY, 'url': url, 'country_code': 'us'}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url



class ExampleSpider(scrapy.Spider):
    name = 'scholar'
    allowed_domains = ['api.scraperapi.com']

    def start_requests(self):
        queries = get_queries()
        for query in queries:
            url = 'https://scholar.google.com/scholar?' + urlencode({'hl': 'en', 'q': query})
            yield scrapy.Request(get_url(url), callback=self.my_parse, meta={'position': 0})

    def parse(self, response):
        print(response.url)
        position = response.meta['position']
        for res in response.xpath('//*[@data-rp]'):
            link = res.xpath('.//h3/a/@href').extract_first()
            temp = res.xpath('.//h3/a//text()').extract()
            if not temp:
                title = "[C] " + "".join(res.xpath('.//h3/span[@id]//text()').extract())
            else:
                title = "".join(temp)
            snippet = "".join(res.xpath('.//*[@class="gs_rs"]//text()').extract())
            cited = res.xpath('.//a[starts-with(text(),"Cited")]/text()').extract_first()
            temp = res.xpath('.//a[starts-with(text(),"Related")]/@href').extract_first()
            related = "https://scholar.google.com" + temp if temp else ""
            num_versions = res.xpath('.//a[contains(text(),"version")]/text()').extract_first()
            published_data = "".join(res.xpath('.//div[@class="gs_a"]//text()').extract())
            position += 1
            item = {'title': title, 'link': link, 'cited': cited, 'relatedLink': related, 'position': position,
                    'numOfVersions': num_versions, 'publishedData': published_data, 'snippet': snippet}
            yield item
        next_page = response.xpath('//td[@align="left"]/a/@href').extract_first()
        if next_page:
            url = "https://scholar.google.com" + next_page
            yield scrapy.Request(get_url(url), callback=self.parse,meta={'position': position})
    
    def my_parse(self, response):
        print(response.url)
        results = response.xpath('//*[@data-rp]')
        if len(results)>=1:
            res = results[0]
        else:
            yield None
        temp = res.xpath('.//h3/a//text()').extract()
        if not temp:
            title = "[C] " + "".join(res.xpath('.//h3/span[@id]//text()').extract())
        else:
            title = "".join(temp)
        
        cited = res.xpath('.//a[starts-with(text(),"Cited")]/text()').extract_first()
        temp = res.xpath('.//a[starts-with(text(),"Related")]/@href').extract_first()
        item = {'title': title,  'cited': cited}
        yield item
