from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from flask import current_app
import os
from io import BytesIO
from time import sleep

class ScreenshotClient:
  def __init__(self):
    if current_app.config['DEBUG']:
      chromedriver_path = '/home/fareed/Documents/Gecko/chromedriver'
    else:
      chromedriver_path = "/app/.chromedriver/bin/chromedriver"
    options = webdriver.ChromeOptions()
    if not current_app.config['DEBUG']:
      chrome_bin = os.environ.get('GOOGLE_CHROME_BIN', "chromedriver")
      options.binary_location = chrome_bin
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    self.driver = webdriver.Chrome(executable_path=chromedriver_path, chrome_options=options)

  def get_screenshot(self, url):
    self.driver.get(url)
    sleep(1.5)
    screenshot = self.driver.get_screenshot_as_png()
    screenshot = BytesIO(screenshot)
    return screenshot