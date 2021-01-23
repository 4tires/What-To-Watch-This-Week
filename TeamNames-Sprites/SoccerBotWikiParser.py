from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import requests
import json
import re

base_url = 'https://www.reddit.com/r/soccerbot/wiki/'

htmlcode = requests.get(base_url + 'index')
soup = BeautifulSoup(htmlcode.text, 'html.parser')
with open('./TeamNames-Sprites/BScontent.txt', 'w') as writefile:
    writefile.write(str(soup))