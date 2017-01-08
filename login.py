#!/usr/local/bin/phantomjs
from selenium import webdriver
import requests


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException

baseurl = "https://learn.bu.edu"
username = "USERNAME"
password = "PASSWORD"

xpaths = { 'usernameTxtBox' : "//*[@id='j_username']",
           'passwordTxtBox' : "//*[@id='j_password']",
           'submitButton' :   "//*[@id='wrapper']/div/form/input"
         }

def init_login():
	mydriver = webdriver.PhantomJS(service_log_path='/Users/melissagarcia/Projects/Python/course-downloader/ghostdriver.log',
									executable_path="/usr/local/bin/phantomjs")
	mydriver.set_window_size(1120, 550)
	mydriver.get(baseurl)
	mydriver.maximize_window()


	#Clear username textbox just in case
	mydriver.find_element_by_xpath(xpaths['usernameTxtBox']).clear()

	# Write username in box
	mydriver.find_element_by_xpath(xpaths['usernameTxtBox']).send_keys(username)

	# Clear password box
	mydriver.find_element_by_xpath(xpaths['passwordTxtBox']).clear()

	# Write password in box
	mydriver.find_element_by_xpath(xpaths['passwordTxtBox']).send_keys(password)

	# Click the login button
	mydriver.find_element_by_xpath(xpaths['submitButton']).click()

	return mydriver


'''
session = requests.Session()
cookies = mydriver.get_cookies()

for cookie in cookies: 
    session.cookies.set(cookie['name'], cookie['value'])

response = session.get("https://learn.bu.edu/webapps/blackboard/content/listContent.jsp?course_id=_33906_1&content_id=_4342559_1")
print(response.text)

mydriver.save_screenshot('out.png');
'''