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


"""
Assumes you run script from What-To-What-This-Week folder.
Uses fslinks.json in What-To-Watch-This_Week\FSJSON folder

Can probably improve by making it navigate the menu items in single browser
rather than opening a new browser for each league via the fslinks.json.
"""

def acha_team_names(url):
    
    url = url + "standings/"
    requests_statuscode = requests.get(url).status_code
    print(requests_statuscode)
    if (str(requests_statuscode) == '404'):
        print("Error code 404. Probably a cup competition.")
        return
    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    #options.add_argument('--headless')

    driver = webdriver.Chrome(executable_path='C:\\Users\micha\Documents\VSCode\What-To-Watch-This-Week\chromedriver.exe', options=options)
    driver.implicitly_wait(30)
    driver.get(url)
    #driver.find_element_by_id('onetrust-button-group-parent').click()
    soup = BeautifulSoup(driver.page_source, features='html.parser')
    attempts = 0
    while  attempts < 5:
        if (soup.find('div', class_='table___21hYPOu undefined')):
            break
        elif(soup.find('div', class_='brackets___1hf5l8s')):
            print('No competition table.')
            driver.quit()
            return
        else:
            soup = BeautifulSoup(driver.page_source, features='html.parser')
            attempts += 1
            time.sleep(.5)
    driver.quit()
    if (attempts >= 5):
        print('No results after 5 attempts.')
        return
    
    thegoodstuff = soup.find_all('div', {'class', 'rows___1BdItrT'})
    if (len(thegoodstuff) != 0):
        TeamNames = []
        for item in thegoodstuff:
            TeamName_aTag = item.find_all('a', class_='rowCellParticipantName___38vskiN')
            for team in TeamName_aTag:
                team = team.contents[0]
                if (' U' in team):
                    u21check = team.split(' U')[-1]
                    if (len(u21check) == 2 and u21check.isdigit()):
                        continue
                TeamNames.append(team)

        if len(TeamNames) == 0:
            return
        #print(TeamNames)
        return TeamNames
    return


def iterate_through_leagues():
    masterjson = {}
    url = 'https://www.flashscore.com'
    with open('FSJSON\\fslinks.json', 'r', encoding='utf8') as openjson:
        jsonfile = json.load(openjson)

        for region in jsonfile['Competitions']:
            if (region not in ['World', 'Europe', 'Africa', 'Asia', 'Australia & Oceania', 'North & Central America', 'South America']):
                for competition, href in jsonfile['Competitions'][region].items():
                    print(region, ":", competition)
                    #print(href)
                    TeamList = acha_team_names(url + href)
                    if (TeamList == None):
                        continue
                    #print(TeamList)
                    if region not in masterjson:
                        TeamNamesList = []
                        for team in TeamList:
                            temp = {}
                            temp['FS_TeamName'] = team
                            TeamNamesList.append(temp)
                        masterjson[region] = TeamNamesList
                        #print(masterjson)
                    else:
                        existingteams = []
                        TeamNamesList = []
                        for item in masterjson[region]:
                            existingteams.append(item['FS_TeamName'])
                        for team in TeamList:
                            if team not in existingteams:
                                temp = {}
                                temp['FS_TeamName'] = team
                                TeamNamesList.append(temp)
                        if (len(TeamNamesList) == 0):
                            print('nothing added')
                        for item in TeamNamesList:
                            masterjson[region].append(item)
                        #masterjson[region].append(TeamNamesList)
                        #print(masterjson)
                    #input('enter')
                    time.sleep(1)

    with open('TeamNames-Sprites\TeamNames-Sprites.json', 'w', encoding='utf8') as teamspritejson:
        json.dump(masterjson, teamspritejson, indent=4, sort_keys=True)
    return

iterate_through_leagues()