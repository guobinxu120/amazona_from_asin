# -*- coding: utf-8 -*-
import scrapy, csv
from scrapy.exceptions import CloseSpider
from scrapy import Request, FormRequest
# from urlparse import urlparse
from datetime import date
import json, requests
import re, random
from collections import OrderedDict

class amazona_from_asinSpider(scrapy.Spider):

	name = "amazona_from_asin_spider"

	use_selenium = False

	total_urls = []

	result_data_list = {}
	total_count = 0

	proxy_text = requests.get('https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt').text
	list_proxy_temp = proxy_text.split('\n')

	list_proxy = []
	for line in list_proxy_temp:
		if line.strip() !='' and (line.strip()[-1] == '+' or line.strip()[-1] == '-'):
			ip = line.strip().split(':')[0].replace(' ', '')
			port = line.split(':')[-1].split(' ')[0]
			list_proxy.append('http://'+ip+':'+port)

###########################################################

	def __init__(self, categories=None, *args, **kwargs):
		super(amazona_from_asinSpider, self).__init__(*args, **kwargs)

		if not categories:
			raise CloseSpider('Received no categories!')
		else:
			self.categories = categories
		self.start_urls = json.loads(self.categories).keys()

		self.headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36'
		}

###########################################################

	def start_requests(self):
		f2 = open('Electric Knives - Knife Sharpeners.csv')

		csv_items = csv.DictReader(f2)
		cat_data = {}

		proxy = random.choice(self.list_proxy)
		url = 'https://www.synccentric.com/features/upc-asin/'

		for i, row in enumerate(csv_items):
			item = OrderedDict()
			item['Category'] = row['Category']
			item['ASIN'] = row['ASIN']
			item['Price'] = row['Price']
			item['Web Hierarchy'] = row['Web Hierarchy']

			form_data = {
				'usr_ip': proxy.replace('http://', ''),
				'identifier': item['ASIN'],
				'locale': 'CA'
			}
			yield FormRequest(url, callback=self.parse, formdata=form_data, dont_filter=True, meta={'item': item, 'proxy':proxy}, errback=self.errCall)

		f2.close()

###########################################################

	def parse(self, response):
		products = response.xpath('//div[@class="product-item-box"]/a')

		#print len(products)
		if not products: return

		for i in products:
			item = {}
			item['Vendedor'] = 512
			item['ID'] = i.xpath('./@href').extract_first().split('-')[-1]
			item['Title'] = i.xpath('./h3/text()').extract_first()

			price = i.xpath('.//span[@class="precio-actual"]/text()').re(r'[\d.,]+')

			if price:
				if price[0] == '.':
					item['Price'] = price[1].replace('.', '')
				else:
					item['Price'] = price[0].replace('.', '')
				item['Currency'] = 'GS'

				item['Category URL'] = response.meta['CatURL']
				item['Details URL'] = response.urljoin(i.xpath('./@href').extract_first())
				item['Date'] = date.today()

				if item['Details URL'] in self.total_urls:
					continue
				self.total_urls.append(item['Details URL'])

				yield item

		response.meta['page_count'] += 1
		next_url = 'https://bristol.com.py/' + response.meta['CatURL'] + '.' + str(response.meta['page_count'])
		if next_url:
			yield Request(response.urljoin(next_url), callback=self.parse, meta=response.meta)
