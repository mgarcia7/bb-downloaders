#!/usr/local/bin/phantomjs
import scrapy
import login
from scrapy.http import Request
import requests
import os
from urllib.parse import unquote
from datetime import datetime,timedelta

class BrickSetSpider(scrapy.Spider):
	name = "brickset_spider"
	base = "https://learn.bu.edu"
	folder_base = "/Users/melissagarcia/Documents/Fall 2016/"
	class_dict = {"EC330":"Algorithms/","BE465":"Senior Design/", "BE467":"Product Design/",
					"BE562":"Comp Bio/", "BE605":"Molecular BioEng/"}
	rsession = None
	start_urls = ['https://learn.bu.edu/webapps/blackboard/execute/modulepage/view?course_id=_33906_1&cmp_tab_id=_98198_1&mode=view',
					'https://learn.bu.edu/webapps/blackboard/execute/modulepage/view?course_id=_33632_1&cmp_tab_id=_97170_1&mode=view',
					'https://learn.bu.edu/webapps/blackboard/execute/modulepage/view?course_id=_35307_1&cmp_tab_id=_102066_1&mode=view',
					'https://learn.bu.edu/webapps/blackboard/execute/modulepage/view?course_id=_35308_1&cmp_tab_id=_102070_1&mode=view',
					'https://learn.bu.edu/webapps/blackboard/execute/modulepage/view?course_id=_33033_1&cmp_tab_id=_95259_1&mode=view']
	cookies = None

	def abs_path(self,class_name,rel_path):
		folder_class_name = self.class_dict[class_name]
		return self.folder_base + folder_class_name + rel_path + "/"

	def download_file(self,url,path_str):
		if self.rsession == None:
			self.rsession = requests.Session()
			for cookie in self.cookies: 
				self.rsession.cookies.set(cookie['name'], cookie['value'])

		resp = self.rsession.get(url,stream=True)
		split_result = resp.url.split("/")
		filename = split_result[-1].split("?")[0]
		filename = path_str+unquote(filename) 
		print(resp.headers)

		if (os.path.lexists(filename)):
			return False
		else:
			os.makedirs(os.path.dirname(filename), exist_ok=True)
			with open(filename, 'wb') as f:
				for chunk in resp.iter_content(chunk_size=1024): 
					if chunk: # filter out keep-alive new chunks
						f.write(chunk)
			return True

	def start_requests(self):
		mydriver = login.init_login()
		self.cookies = mydriver.get_cookies()
		mydriver.save_screenshot('out.png');

		for url in self.start_urls:
			yield Request(url, cookies=self.cookies, callback=self.parse)

	def parse(self, response):
		SET_SELECTOR = "//ul[@id='courseMenuPalette_contents']/li"
		for brickset in response.xpath(SET_SELECTOR):
			NAME_SELECTOR = 'a ::text'
			LINK_SELECTOR = 'a::attr(href)'
			yield {
				'name': brickset.css(NAME_SELECTOR).extract_first(),
				'link': brickset.css(LINK_SELECTOR).extract_first()
			}

			
			NEXT_PAGE_SELECTOR = 'a::attr(href)'
			next_page = brickset.css(NEXT_PAGE_SELECTOR).extract_first()
			if next_page:
				print("here")
				yield scrapy.Request(
					self.base+next_page,
					cookies=self.cookies,
					callback=self.parse_content
		    	)

	def parse_content(self,response):
		SET_SELECTOR = "//ul[@id='content_listContainer']//a"
		#SET_SELECTOR = "//div[@class='item clearfix']/a"
		CLASS_NAME_SELECTOR = "//li[@class='root coursePath']/a/text()"
		PAGE_NAME_SELECTOR = "//h1[@id='pageTitleHeader']/span[@id='pageTitleText']/text()"

		TITLE_SELECTOR = "//title/text()"
		PATH_SELECTOR = "//ol[@class='clearfix']/li"

		title = response.xpath(TITLE_SELECTOR).extract_first()
		_,class_name = title.split(" – ")
		class_name = class_name[:5]

		path_str = [u"".join(li.xpath('.//text()').extract()) for li in response.xpath(PATH_SELECTOR)]
		path_str = [item.strip().replace(u"\r\n",'') for item in path_str]
		path_str = "/".join(path_str[1:])


		for brickset in response.xpath(SET_SELECTOR):
			NAME_SELECTOR = 'span ::text'
			LINK_SELECTOR = '::attr(href)'

			name = brickset.css(NAME_SELECTOR).extract_first()
			yield {
				'name': name,
				'link': brickset.css(LINK_SELECTOR).extract_first(),
				'class_name': class_name,
				'path': path_str
			}

			NEXT_PAGE_SELECTOR = 'a::attr(href)'
			next_page = brickset.css(NEXT_PAGE_SELECTOR).extract_first()
			if next_page != None and "/webapps/blackboard/content" in next_page:
				yield scrapy.Request(
					self.base+next_page,
					cookies=self.cookies,
					callback=self.parse_content
		    	)
			elif next_page != None and "/bbcswebdav/pid" in next_page:
				url = self.base + next_page
				if name == None:
					name = "dk"
				fn = self.abs_path(class_name,path_str)
				self.download_file(url,fn)



