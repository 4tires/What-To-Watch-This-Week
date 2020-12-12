import csv
from bs4 import BeautifulSoup
import json
import string

competitiondict = {'ENGLAND': {'Premier League': 4}, 'FRANCE': {'Ligue 1': 1}, 'GERMANY': {'Bundesliga': 5}, 'NETHERLANDS': {'Eredivisie': 2}, 'SPAIN': {'LaLiga': 2}, 'RÉUNION': {'Regionale 1': 1}, 'ITALY': 
{'Serie A': 1}, 'BELGIUM': {'Jupiler League': 1}}

url = "https://www.flashscore.com"

def parser(compdict):
    matchesdict = {}
    with open('listas.csv','r') as li:
        listas = csv.reader(li)
        for place in compdict:
            country = place
            for comp in compdict[place]:
                competition = comp
                comp_count = compdict[place][comp]
                href = linkgetter(country,competition)
                #results = request.get(url + href)
                for match in listas:
                    if (match == []):
                        pass
                    else:
                        print(match, url + href + 'fixtures/')
                  

    return

def loadcsv(csvfile):
        for match in matches:
            if (match == []):
                pass
            else:
                print(match)
        
#loadcsv("listas.csv")

def linkgetter(country, competition):
    country_proper = string.capwords(country)
    if (competition.find(' - Group Stage')):
        comp_proper = competition.replace(' - Group Stage', '')
    else:
        comp_proper = competition
    with open('FSJSON/flasklinks.json', 'r') as fs:
        fsjson = json.load(fs)
        href = fsjson['Competitions'][country_proper][comp_proper]
        return href

parser(competitiondict)