# -*- coding: utf-8 -*-

import scrapy, requests, csv, random
# from urlparse import urlparse
from collections import OrderedDict
from scrapy import Request, FormRequest

class upc(scrapy.Spider):

	name = "upc"
	start_urls = ('https://bristol.com.py/',)

	use_selenium = False

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


	def parse(self, response):
		item = response.meta['item']
		item['UPC'] = ''
		vals = response.xpath('//div[@class="col-sm-8"]//text()').extract()
		for i, val in enumerate(vals):
			val = val.strip()
			if 'UPC' in val:
				item['UPC'] = vals[i + 1]
		if not item['UPC']:
			ban_proxy = response.request.meta['proxy']
			if '154.16.' in ban_proxy:
				ban_proxy = ban_proxy.replace('http://', 'http://eolivr4:bntlyy3@')
			if ban_proxy in self.list_proxy:
				self.list_proxy.remove(ban_proxy)
			if len(self.list_proxy) < 1:
				proxy_text = requests.get('https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt').text
				list_proxy_temp = proxy_text.split('\n')
				self.list_proxy = []
				for line in list_proxy_temp:
					if line.strip() !='' and (line.strip()[-1] == '+' or line.strip()[-1] == '-'):
						ip = line.strip().split(':')[0].replace(' ', '')
						port = line.split(':')[-1].split(' ')[0]
						self.list_proxy.append('http://'+ip+':'+port)

			proxy = random.choice(self.list_proxy)
			# response.request.meta['proxy'] = proxy
			print ('err proxy: ' + proxy)
			if not 'errpg' in response.request.url :
				yield Request(response.request.url,
							  callback=self.parse,
							  meta={'proxy': proxy, 'item':response.request.meta['item']},
							  dont_filter=True,
							  errback=self.errCall)
			# self.errCall(response)
			# if response.xpath('//div[@role="alert"]/text()').extract_first() == 'This search is limited to 10 requests per hour. For unlimited searches, please ':
			# 	self.errCall(response)
			# 	return
		else:
			yield item


	def errCall(self, response):
		# try:
		#     if response.value.response.xpath('//pre/text()').extract_first() != 'Retry later\n':
		#         print('no result: {}'.format(response.request.meta['ean']))
		#         return
		# except:
		#     pass
		ban_proxy = response.request.meta['proxy']
		if '154.16.' in ban_proxy:
			ban_proxy = ban_proxy.replace('http://', 'http://eolivr4:bntlyy3@')
		if ban_proxy in self.list_proxy:
			self.list_proxy.remove(ban_proxy)
		if len(self.list_proxy) < 1:
			proxy_text = requests.get('https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt').text
			list_proxy_temp = proxy_text.split('\n')
			self.list_proxy = []
			for line in list_proxy_temp:
				if line.strip() !='' and (line.strip()[-1] == '+' or line.strip()[-1] == '-'):
					ip = line.strip().split(':')[0].replace(' ', '')
					port = line.split(':')[-1].split(' ')[0]
					self.list_proxy.append('http://'+ip+':'+port)

		proxy = random.choice(self.list_proxy)
		# response.request.meta['proxy'] = proxy
		print ('err proxy: ' + proxy)
		if not 'errpg' in response.request.url :
			yield Request(response.request.url,
						  callback=self.parse,
						  meta={'proxy': proxy, 'item':response.request.meta['item']},
						  dont_filter=True,
						  errback=self.errCall)
