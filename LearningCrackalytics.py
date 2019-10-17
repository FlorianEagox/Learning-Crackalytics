import yaml
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
import json

with open('config.yaml', 'r') as file:
	config = yaml.safe_load(file)

knowledge_base = {}
browser = None  # webdriver.Firefox()


def minify(string): return "".join(e for e in string if e.isalnum()).lower()


def navigate_to_session():
	# Signing in
	browser.get(config['url'])  # Open the Learning Catalytics Page
	browser.find_element_by_css_selector("#user_username").send_keys(config['username'])
	browser.find_element_by_css_selector("#user_password").send_keys(config['password'] + Keys.RETURN)

	# Select the current session
	try:
		browser.find_element_by_css_selector(".join_class_session_link").click()  # Click on the ongoing session
	except NoSuchElementException:
		print('no sessions are taking place right now... Trying again')

	# Don't select a seat
	browser.find_element_by_link_text("I can't find my seat").click()


def find_answer_from_quizlet(url, question):
	page = BeautifulSoup(requests.get(url).content, 'html.parser')
	for el in page.select('.SetPageTerm-content'):
		if minify(question) in minify(el.get_text()) and minify(question) not in knowledge_base:
			knowledge_base[minify(question)] = minify(el.select('*')[-1].get_text())


def get_search_results(question):
	querystring = {'cx': config['cse_cx'], "key": config['cse_key'], 'q': question}
	results = json.loads(requests.request("GET", config['cse_request_url'], params=querystring).text)
	return [item['link'] for item in results['items']]


# navigate_to_session()
question = 'On Aug. 5, 2017, Venus is in Gemini from Earth. If you stand on Venus, which constellation is Earth in'
answer = ""
for url in get_search_results(question):
	if minify(question) not in knowledge_base:
		find_answer_from_quizlet(url, question)
		print(knowledge_base)
print(knowledge_base[minify(question)])
