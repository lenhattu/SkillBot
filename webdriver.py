from selenium import webdriver
import selenium.webdriver.chrome.options as chrome_options
import selenium.webdriver.firefox.options as firefox_options
import re
import json
import string


PATH_CHROME_DRIVER = r"chromedriver.exe"
PATH_FIREFOX_DRIVER = r"./geckodriver"
PATH_FIREFOX_DRIVER1 = r"./geckodriver1"


def get_firefox():
    options = firefox_options.Options()
    options.headless = True
    fp = webdriver.FirefoxProfile(
        '/home/tule/.mozilla/firefox/ft125k6g.default')
    driver = webdriver.Firefox(options=options, firefox_profile=fp, executable_path=PATH_FIREFOX_DRIVER)
    return driver


def get_firefox1():
    options = firefox_options.Options()
    options.headless = True
    fp = webdriver.FirefoxProfile(
        '/home/tule/.mozilla/firefox/4do90hmw.tnl6wk')
    driver = webdriver.Firefox(options=options, firefox_profile=fp, executable_path=PATH_FIREFOX_DRIVER1)
    return driver
