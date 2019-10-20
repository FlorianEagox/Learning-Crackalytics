import json
import time
import requests
import schedule
import yaml
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

with open('config.yaml', 'r') as file:
	config = yaml.safe_load(file)

knowledge_base = {}
switch_dates = {'MON': schedule.every().monday,
				'TUE': schedule.every().monday,
				'WED': schedule.every().wednesday,
				'THU': schedule.every().thursday,
				'FRI': schedule.every().friday,
				'SAT': schedule.every().saturday,
				'SUN': schedule.every().sunday}


def minify(string): return ''.join(e for e in string if e.isalnum()).lower()


def navigate_session():
	refresh = 15
	browser = webdriver.Firefox(executable_path=config['geckodriver_path'], keep_alive=False)
	browser.get(config['url'])  # Open the Learning Catalytics Page
	if browser.find_elements_by_id('user_username') and browser.find_elements_by_id('user_password'):
		browser.find_element_by_id('user_username').send_keys(config['username'])
		browser.find_element_by_id('user_password').send_keys(config['password'] + Keys.RETURN)
	session_active = True
	while session_active:
		if browser.current_url.split('/')[-1] == 'class_sessions':
			# Select the current session
			sessions = browser.find_elements_by_css_selector('.join_class_session_link')
			if sessions:
				sessions[0].click()  # Click on the ongoing session
				refresh = 5
			else:
				browser.refresh()
		elif browser.current_url.split('/')[-1] == 'select_seat':
			browser.find_element_by_link_text("I can't find my seat").click()
		elif browser.current_url.split('/')[-1].isnumeric():
			if browser.find_elements_by_id('responses'):
				question = browser.find_element_by_css_selector('.item_prompt_container label').text
				answer = ask_question(question)
				print(answer)
				for choice in browser.find_elements_by_css_selector('.multiplechoice p'):
					if minify(choice.text) in answer or answer in minify(choice.text):
						choice.click()
			else:
				print('waiting for question')
		elif browser.current_url.split('/')[-1] == 'post_session':
			session_active = False
			print(browser.find_element_by_id('score_summary').text)
		time.sleep(refresh)


def find_answer_from_quizlet(url):
	page = BeautifulSoup(requests.get(url).content, 'html.parser')
	for el in [el.select('*') for el in page.select('.SetPageTerm-content')]:
		knowledge_base[minify(el[0].get_text())] = minify(el[-1].get_text())


def get_search_results(question):
	querystring = {'cx': config['cse_cx'], 'key': config['cse_key'], 'q': question}
	results = json.loads(requests.request('GET', config['cse_request_url'], params=querystring).text)
	return [item['link'] for item in results['items']]


def ask_question(question):
	found_answer = []
	for url in get_search_results(question):
		found_answer = [key for key in knowledge_base if minify(question) in key]
		if not found_answer:
			find_answer_from_quizlet(url)
	if found_answer:
		return knowledge_base[found_answer[0]]
	return found_answer

navigate_session()
for times in config['times']:
	switch_dates[times['day']].at(times['time']).do(navigate_session)
while True:
	schedule.run_pending()
	time.sleep(1)
