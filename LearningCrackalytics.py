import yaml
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

with open('config.yaml', 'r') as file:
	config = yaml.safe_load(file)

browser = webdriver.Firefox()

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
