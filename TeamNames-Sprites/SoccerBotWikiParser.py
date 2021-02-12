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
soccer wiki sprites https://www.reddit.com/r/soccerbot/wiki/index
"""
base_url = 'https://www.reddit.com'
"""
r = requests.get(base_url + 'index')
soup = BeautifulSoup(r.text, 'html.parser')
soup = soup.body
with open('./TeamNames-Sprites/BScontent.txt', 'w', encoding='utf8') as writefile:
    writefile.write(r.text)
"""
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
options.add_experimental_option("prefs", { 
    "profile.default_content_setting_values.notifications": 2}) 
#options.add_argument('--headless')

driver = webdriver.Chrome(executable_path='C:\\Users\micha\Documents\VSCode\What-To-Watch-This-Week\chromedriver.exe', options=options)
driver.implicitly_wait(30)
competitionsDict = {}
TeamNameSpriteDict = {}
TeamNameSpriteDict['National Teams'] = {}


def main():
    driver.get(base_url + '/r/soccerbot/wiki/index')
    #input('Enter to continue')
    soup = BeautifulSoup(driver.page_source, features='html.parser')
    soup = soup.find('div', class_='md wiki').find_all('ul')[2].find_all('a')

    for continent in soup:
        continentName = str(continent.get_text())
        #TeamNameSpriteDict[continentName] = {}
        TeamNameSpriteDict['National Teams'][continentName] = {}
        competitionsDict[continentName] = {}
        country_parser(str(continent['href']), continentName)

    driver.quit()
    print(TeamNameSpriteDict)
    with open('./TeamNames-Sprites/soccerbot-TeamNameSprites.json', 'w', encoding='utf8') as wr:
        json.dump(TeamNameSpriteDict, wr, indent=4, sort_keys=True)

    print(competitionsDict)
    with open('./TeamNames-Sprites/soccerbot-CompetitionSprites.json', 'w', encoding='utf8') as wr:
        json.dump(competitionsDict, wr, indent=4, sort_keys=True)
    #with open('./TeamNames-Sprites/BScontent.txt', 'w', encoding='utf8') as writefile:
    #    writefile.write(str(soup))
    return
    
def country_parser(continentURLIn, continentIn):
    driver.get(base_url + continentURLIn)
    soup = BeautifulSoup(driver.page_source, features='html.parser')

    continentCompSoup = soup.find_all('tr')
    for comp in continentCompSoup[1:]:
        comp = comp.find_all('td')
        if (comp[3].contents != []):
            sprite = comp[3].contents[0].contents[0]
        else:
            sprite = None
        competitionsDict[continentIn][comp[1].get_text()] = sprite
    
    countrySoup = soup.find('div', class_='md wiki').find_all('ul')[2].find_all('a')
    for country in countrySoup:
        countryName = str(country.get_text())
        TeamNameSpriteDict[countryName] = {}
        competitionsDict[countryName] = {}
        time.sleep(1)
        teamComp_parser(str(country['href']), countryName, continentIn)
    return

def teamComp_parser(countryURLIn, countryIn, continentIn):
    driver.get(base_url + countryURLIn)
    soup = BeautifulSoup(driver.page_source, features='html.parser')
    with open('./TeamNames-Sprites/BScontent.txt', 'w', encoding='utf8') as writefile:
        writefile.write(str(soup))
    soup = soup.find('div', class_='md wiki')
    if (soup.find('h2', id='wiki_national_team')):
        nTHeader = soup.find('h2', id='wiki_national_team')
        nTTable = nTHeader.find_next_sibling('table')
        nTTable = nTTable.find('tbody').find_all('td')
        if (nTTable[4].contents != []):
            sprite = nTTable[4].contents[0].contents[0]
        else:
            sprite = None
        TeamNameSpriteDict['National Teams'][continentIn][nTTable[1].get_text()] = sprite
    if (soup.find('h2', id='wiki_clubs')):
        
        clubsHeader = soup.find('h2', id='wiki_clubs')
        clubsListSoup = clubsHeader.find_next_sibling('table')
        clubsListSoup = clubsListSoup.find('tbody').find_all('tr')

        #clubsListSoup = soup.find_all('tbody')[1].find_all('tr')
        for club in clubsListSoup:
            club = club.find_all('td')
            if (club[4].contents != []):
                sprite = club[4].contents[0].contents[0]
            else:
                sprite = None
            TeamNameSpriteDict[countryIn][club[1].get_text()] = sprite
    if (soup.find('h2', id='wiki_competitions')):
        
        compHeader = soup.find('h2', id='wiki_competitions')
        compListSoup = compHeader.find_next_sibling('table')
        compListSoup = compListSoup.find('tbody').find_all('tr')

        #compListSoup = soup.find_all('tbody')[2].find_all('tr')
        for comp in compListSoup:
            comp = comp.find_all('td')
            if (comp[3].contents != []):
                sprite = comp[3].contents[0].contents[0]
            else:
                sprite = None
            competitionsDict[countryIn][comp[1].get_text()] = sprite
    with open('./TeamNames-Sprites/soccerbot-TeamNameSprites.json', 'w', encoding='utf8') as wr:
        json.dump(TeamNameSpriteDict, wr, indent=4, sort_keys=True)


    with open('./TeamNames-Sprites/soccerbot-CompetitionSprites.json', 'w', encoding='utf8') as wr:
        json.dump(competitionsDict, wr, indent=4, sort_keys=True)

#main()

"""
with open('./TeamNames-Sprites/BScontent.txt', 'w', encoding='utf8') as writefile:
    writefile.write(str(soup))
"""

def shifter():
    with open('./TeamNames-Sprites/soccerbot-TeamNameSprites.json', 'r', encoding='utf8') as rf:
        tNSJSON = json.load(rf)
    for region in list(tNSJSON):
        if region in ['National Teams']:
            continue
        for item in tNSJSON[region]:
            tNSJSON[item] = tNSJSON[region][item]
        del tNSJSON[region]
    with open('./TeamNames-Sprites/soccerbot-TeamNameSprites.json', 'w', encoding='utf8') as rf:
        json.dump(tNSJSON, rf, indent=4, sort_keys=True)
    return
