from bs4 import BeautifulSoup
import json
import requests
import re

"""
Assumes you run this file from the "What-To-Watch-This-Week" folder
"""

url = "https://www.flashscore.com"

def country_parser():
    results = requests.get(url)
    soup = BeautifulSoup(results.text, 'html.parser')
    country_menu = soup.find_all('ul', class_='tournament-menu')
    json_dict = {'Competitions': {}}
    for submenu in country_menu:
        countries = submenu.find_all('li', id=re.compile('^lmenu'))
        for country in countries:
            country_name = country.find('a',href=True).get_text()
            country_href = country.find('a', href=True)['href']
            json_dict['Competitions'].update(league_parser(country_href, country_name))
    with open('./FSJSON/fslinks.json','w') as fslinks:
        json.dump(json_dict, fslinks, indent=4, sort_keys=True)

def league_parser(href, country):
    results = requests.get(url + href)
    dict = {str(country): {}}
    temp = {}
    soup = BeautifulSoup(results.text, 'html.parser')
    list = soup.find('ul', class_='selected-country-list')
    competitions = list.find_all('li')
    for competition in competitions:
        if (competition['class'] in [[], ['last'], ['hidden-templates'], ['last', 'hidden-templates']]):
            comp_name = competition.get_text()
            comp_href = competition.find('a', href=True)['href']
            temp = { str(comp_name) : str(comp_href)}
            dict[str(country)].update(temp)
    print(country + " dictionary completed.")
    return dict

country_parser()