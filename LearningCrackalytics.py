import yaml
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

with open('config.yaml', 'r') as file:
	config = yaml.safe_load(file)

browser = webdriver.Firefox()

# Signing in
browser.get(config['url'])  # Open the Learning Catalytics Page
browser.find_element_by_css_selector("#user_username").send_keys(config['username'])
browser.find_element_by_css_selector("#user_password").send_keys(config['password'] + Keys.RETURN)
