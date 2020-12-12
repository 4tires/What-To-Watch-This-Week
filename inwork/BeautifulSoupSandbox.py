from bs4.dammit import UnicodeDammit
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
from login_credentials import username_credential, password_credential
import tempfile, shutil
import json
import requests
import re


url1 = "https://www.flashscore.com/football/spain/laliga/fixtures/"


def parser():
    results = requests.get(url1)
    soup = BeautifulSoup(results.text, 'html.parser')
    matches = soup.find('div', id='tournament-page-data-fixtures').contents
    with open('flashscore.txt','w', encoding='utf-8') as fs:
        fs.write(str(matches))

def csver():
    results = requests.get(url1)
    soup = BeautifulSoup(results.text, 'html.parser')
    matches = soup.find('div', id='tournament-page-data-fixtures').contents
    matches = str(matches[0]).split("~")
    matches = matches[2:]
    #game = matches[3].split("¬")
    gamelist= []
    for games in matches:
        temp = {}
        if (games != ''):
            match = str(games).split("¬")
            for item in match:
                if (item != ''):
                    if str(item.split("÷")[0] + "÷") in ['ER÷', 'AE÷', 'AF÷']:
                        temp[str(item.split("÷")[0] + "÷")] = str(item.split("÷")[1])
                        gamelist.append(temp)
    print(gamelist)

    #for item in game:
    #    if (item != ''):
    #        print(item.split("÷")[1])
    #for item in game:
        #gamedict[str(item).split("÷")[0] + "÷")] = str(item.split("÷")[1])
    #print(gamedict)

csver()
#parser()

""" #THIS FUNCTION PARSES WHATEVER PAGE IN UTF-8 FORMAT. DO NOT CHANGE
def page_parser():
    results = requests.get(url1)
    soup = BeautifulSoup(results.text, 'html.parser')

    with open('flashscore.txt', 'w', encoding='utf-8') as fs:
        fs.write(str(soup.prettify()))
"""