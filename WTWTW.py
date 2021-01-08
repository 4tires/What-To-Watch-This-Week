from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
from login_credentials import username_credential, password_credential
import requests
from json import load

url = "https://www.flashscore.com/"

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Chrome(executable_path='C:\\Users\\paulo\\OneDrive\\Documentos\\Programação\\chromedriver.exe', chrome_options=options)
driver.implicitly_wait(30)
driver.get(url)

driver.find_element_by_id('signIn').click()

try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "login-content"))
    )
finally:
    print("Login")

time.sleep(3)
username = driver.find_element_by_id("email")
username.clear()
username.send_keys(username_credential)

password = driver.find_element_by_name("password")
password.clear()
password.send_keys(password_credential)

driver.find_element_by_id('login').click()
with open ('listas.csv', 'w', newline='') as listas:
	pass

def parser(competitions_dict):
	checked_matches = []
	soup = BeautifulSoup(driver.page_source, 'html.parser')

	n = 0
	while n < 5:
		if soup.find('div', class_='sportName soccer'):
			break
		else:
			soup = BeautifulSoup(driver.page_source, 'html.parser')
			n += 1
		if n >= 5:
			print("failure to acquire match info.")
			break
		time.sleep(0.5)

	date = soup.find('div', class_='calendar__datepicker').get_text()#.split(' ')[0].replace('/', '.')
	matches = soup.find_all('div', class_='checked')
	list_of_matches = []
	for match in matches:
		list_of_matches.append(match.find_parent('div', class_='event__match'))
	list_matches = list(filter(None, list_of_matches))
	for match in list_matches:
		temp = {}
		try:
			time = match.find('div', class_='event__time').get_text().replace(":", "")
		except:
			time = "No time"
		home_team = match.find('div', class_='event__participant--home').get_text()
		away_team = match.find('div', class_='event__participant--away').get_text()
		competition = match.find_previous_sibling('div', class_ = "event__header").find('span', class_ = "event__title--name").get_text()
		region = match.find_previous_sibling('div', class_ = "event__header").find('span', class_ = "event__title--type").get_text()
		if (region in competitions_dict):
			if (competition in competitions_dict[region]):
				pass
			else:
				competitions_dict[region].append(competition)
		else:
			competitions_dict[region] = [competition]		
		temp['Time'] = time
		temp['Home'] = home_team
		temp['Away'] = away_team
		temp['Region'] = region
		temp['Competition'] = competition
		checked_matches.append(temp)
	print("Completed day")
	return date, checked_matches

def fetcher():
	days = 7
	WTWTWdict = {}
	competitions_dict = {}
	for n in range(days):
		date, checked_matches = parser(competitions_dict)
		WTWTWdict[date] = checked_matches
		if n == (days - 1):
			driver.quit()
			print("Completed all parsers")
			return WTWTWdict, competitions_dict
		driver.find_element_by_class_name('calendar__direction--tomorrow').click()
		time.sleep(1)

def competition_matches(region, competition):
	gamelist = []
	href, competition_proper = acha_link_e_arranja_nome(region, competition)
	results = requests.get(url + href + 'fixtures')
	soup = BeautifulSoup(results.text, 'html.parser')
	matches = soup.find('div', id='tournament-page-data-fixtures').contents
	temp = str(matches[0]).split('~')[2:]
	muitos_matches = []
	for n in range(len(temp)):
		if ('AE÷'  in temp[n]):
			muitos_matches.append(temp[n])
	for match in muitos_matches:
		temp = {}
		if (match != ''):
			match = str(match).split('¬')
			for item in match:
				if (item != ''):
					if str(item.split("÷")[0] + "÷") in ['ER÷', 'AE÷', 'AF÷', 'AM÷']:
						temp[str(item.split("÷")[0] + "÷")] = str(item.split("÷")[1])				
			gamelist.append(temp)
	return gamelist, competition_proper

def acha_link_e_arranja_nome(region, competition):
	region_proper = region
	competition_proper = ''
	with open('FSJSON/fslinks.json','r') as fs:
		fsjson = load(fs)
		for key in fsjson['Competitions']:
			if region_proper.lower() == key.lower():
				region_proper = key
				break
		if ('-' in competition):
			competition_name_split = competition.split(' - ')
			for n in range(len(competition_name_split)):
				competition_proper = ' - '.join(competition_name_split[:n+1])
				for key in fsjson['Competitions'][region_proper]:
					if (competition_proper == key):
						href = fsjson['Competitions'][region_proper][competition_proper]
						return href, competition_proper
		else:
			competition_proper = competition
			href = fsjson['Competitions'][region_proper][competition_proper]
			return href, competition_proper
		
def acha_round_e_aggregate(home, away, gamelist):
	fs_round_translator = {'1/32-finals':'Round of 64','1/16-finals':'Round of 32', '1/8-finals':'Round of 16'}
	round = ''
	aggregate = ''
	for item in gamelist:
		try:
			if (item['AE÷'] == home and item['AF÷'] == away):
				if ("Round " not in item['ER÷'] and len(item['ER÷']) not in [7, 8]):
					round = item['ER÷']
					if round in fs_round_translator.keys():
						round = fs_round_translator[round]
				if ('AM÷' in item):
					aggregate = item['AM÷']
				return round, aggregate
		except:
			print("Error Occurred at " + home + ", " + away)
			return "Error with gamelist.", aggregate
	print("No results for " + home + " vs " + away + " round and aggregate score.")
	return "no-round-data", "no-aggregate-data"

def match_details(competitions_dict, WTWTWmatches):
	print('Adding rounds and aggregate scores')
	for region in competitions_dict:
		for competition in competitions_dict[region]:
			gamelist, competition_proper = competition_matches(region, competition)
			for date in WTWTWmatches:
				for match in WTWTWmatches[date]:
					if (match['Region'] == region and match['Competition'] == competition):
						round, aggregate = acha_round_e_aggregate(match['Home'], match['Away'], gamelist)
						match['Round'] = round
						match['Aggregate'] = aggregate
						match['Competition'] = competition_proper
		
def WTWTW():
	WTWTWmatches, competitions_dict = fetcher()
	match_details(competitions_dict, WTWTWmatches)

	print("Writing listas.csv")
	with open('listas.csv', 'a', newline='', encoding='utf8') as listas:
		writer = csv.writer(listas, delimiter=';')
		for date in WTWTWmatches:
			for match in sorted(WTWTWmatches[date], key=lambda i: i['Time']):
				writer.writerow([match['Time'], match['Home'], match['Away'], match['Competition'], match['Round'], match['Aggregate']])
			writer.writerow([])
	print("Finished running WTWTW")
	return WTWTWmatches

input('Press Enter to Continue...')
WTWTW()
