from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
from login_credentials import username_credential, password_credential, chromedriver_path
from json import load

url = "https://www.flashscore.com/"

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Chrome(executable_path=chromedriver_path, options=options)
driver.implicitly_wait(30)
driver.get(url)
wait = WebDriverWait(driver, 10)

driver.find_element_by_id('signIn').click()

try:
    element = wait.until(
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

def parser(competitions_dict):
	checked_matches = []
	wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'event__titleBox')))
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	date = soup.find('div', class_='calendar__datepicker').get_text()#.split(' ')[0].replace('/', '.')
	matches = soup.find_all('svg', class_='active___3hdtOBF')
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
		temp['id'] = match['id']
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
			print("Completed all parsers")
			return WTWTWdict, competitions_dict
		driver.find_element_by_class_name('calendar__direction--tomorrow').click()
		time.sleep(2)

def match_details(competitions_dict, WTWTWmatches):
	continentList = ['Asia', 'Africa', 'Europe', 'North & Central America', 'South America', 'Australia & Oceania', 'World']
	print('Fetching match round and aggregate score.')
	with open('./TeamNames-Sprites/CompNames-Sprites.json', 'r', encoding='utf8') as rf:
		cNSDict = load(rf)
	for region in competitions_dict:
		for competition in competitions_dict[region]:
			isCup = 0
			gamelist, compProperName, regionProperName = competition_matches(region, competition)
			for date in WTWTWmatches:
				for match in WTWTWmatches[date]:
					if (match['Region'] == region and match['Competition'] == competition):
						round = AchaRound(match['Home'], match['Away'], gamelist) if gamelist != None else None
						match['Round'] = round
						if round != None:
							isCup = 1
			if isCup == 1:
				driver.find_element_by_id('li1').click()
				wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".nmf__title, .event__participant")))
				for date in WTWTWmatches:
					for match in WTWTWmatches[date]:
						if match['Region'] == region and match['Competition'] == competition:
							if match['Round'] != None:
								aggregate = AchaAggregate(match['Home'], match['Away'], match['Round'])
								match['H FL Score'] = aggregate[1]
								match['A FL Score'] = aggregate[0]
				driver.find_element_by_id('li2').click()
				wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'event__participant')))
			for date in WTWTWmatches:
				for match in WTWTWmatches[date]:
					if (match['Region'] == region and match['Competition'] == competition):
						match['Region'] = regionProperName
						match['Competition'] = compProperName
						if compProperName in list(cNSDict[regionProperName].keys()):
							match['C Sprite'] = cNSDict[regionProperName][compProperName]['Sprite']
							tempCompProperName = cNSDict[regionProperName][compProperName]['Proper']
							match['Competition'] = (tempCompProperName if tempCompProperName != None else compProperName)
							compProperName = (tempCompProperName if tempCompProperName != None else compProperName)
						else:
							match['C Sprite'] = None

						if regionProperName in continentList:
							nameSpriteDict = NameAndSprite(match, 1)
						else:
							nameSpriteDict = NameAndSprite(match, 0)
						match['Home'] = nameSpriteDict['H Name'] if nameSpriteDict['H Name'] != None else match['Home']
						match['Away'] = nameSpriteDict['A Name'] if nameSpriteDict['A Name'] != None else match['Away']
						for side in ['Home', 'Away']:
							if ' (' in match[side] and ' (Am)' not in match[side]:
								match[side] = match[side][0:match[side].find(' (')]
						match['H Sprite'] = nameSpriteDict['H Sprite']
						match['A Sprite'] = nameSpriteDict['A Sprite']

	return WTWTWmatches

def competition_matches(region, competition):
	href, competition_proper, region_proper = AchaLinkEArranjaCompNome(region, competition)
	if href != None:
		driver.get(url + href + 'fixtures')
		soup = BeautifulSoup(driver.page_source, 'html.parser')
		checkedMatchesListUnfiltered = []
		checkedMatches = soup.find_all('svg', class_='active___3hdtOBF')
		for match in checkedMatches:
			checkedMatchesListUnfiltered.append(match.find_parent('div', class_='event__match'))
		returnCheckedMatchesList = list(filter(None, checkedMatchesListUnfiltered))
		return returnCheckedMatchesList, competition_proper, region_proper
	else:
		return None, competition_proper, region_proper

def AchaLinkEArranjaCompNome(region, competition):
	region_proper = region
	competition_proper = competition
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
			if competition_proper in list(fsjson['Competitions'][region_proper].keys()):
				href = fsjson['Competitions'][region_proper][competition_proper]
				return href, competition_proper, region_proper
	elif competition_proper in list(fsjson['Competitions'][region_proper].keys()):
		href = fsjson['Competitions'][region_proper][competition_proper]
		return href, competition_proper, region_proper
	else:
		print("MISSING COMPETITION! No href found for", competition_proper, "in", region_proper)
		return None, competition_proper, region_proper
	print("Error: No matching competition found for", competition_proper, "in", region_proper)
	return None, competition_proper, region_proper

def AchaRound(home, away, gamelist):
	#fs_round_translator = {'1/32-finals':'Round of 64','1/16-finals':'Round of 32', '1/8-finals':'Round of 16'}
	round = None
	for item in gamelist:
		home_team = item.find('div', class_='event__participant--home').get_text()
		away_team = item.find('div', class_='event__participant--away').get_text()
		if (home_team == home and away_team == away):
			round = item.find_previous_sibling('div', class_='event__round')
			round = (round.get_text() if round != None else None)
			if round != None:
				if ("Round " in round[:6] and len(round) in [7, 8]):
					round = None
			return round
	print("No results for " + home + " vs " + away + " round.")
	return round

def AchaAggregate(homeTeam, awayTeam, roundName):
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	tableRoundHeader = soup.find('div', text=roundName)
	fLScoreHome = None
	fLScoreAway = None
	if tableRoundHeader != None:
		row = tableRoundHeader
		while True:
			row = row.next_sibling
			if row == None:
				break
			elif any(item in ['event__round', 'event__header'] for item in row['class']):
				break
			else:
				fLHome = row.find('div', class_='event__participant--home').get_text()
				fLAway = row.find('div', class_='event__participant--away').get_text()
				if ((fLHome == awayTeam) and (fLAway == homeTeam)):
					fLScore = row.find('div', class_='event__scores').find_all('span')
					fLScoreHome = fLScore[0].get_text()
					fLScoreAway = fLScore[1].get_text()
					break
	return [fLScoreHome, fLScoreAway]

def NameAndSprite(matchDict, intlGame):
	region = matchDict['Region']
	nameSpriteDict = {}
	nameSpriteDict['Home'] = {
		'Name' : matchDict['Home'],
		'Proper' : None,
		'Sprite' : None,
		'h2h' : 'h2h_home'
	}
	nameSpriteDict['Away'] = {
		'Name' : matchDict['Away'],
		'Proper' : None,
		'Sprite' : None,
		'h2h' : 'h2h_away'
	}
	returnDict = {
		'H Name' : None,
		'H Sprite' : None,
		'A Name' : None,
		'A Sprite' : None
	}
	# 1 if international competition. 0 if not.
	with open('./TeamNames-Sprites/TeamNames-Sprites-V2.json', 'r', encoding='utf8') as rf:
		tNSDict = load(rf)
	if not intlGame:
		for side in list(nameSpriteDict.keys()):
			teamName = nameSpriteDict[side]['Name']
			try:
				tNSDict[region][teamName]
				nameSpriteDict[side]['Proper'] = tNSDict[region][teamName]['Proper']
				nameSpriteDict[side]['Sprite'] = tNSDict[region][teamName]['Sprite']
				continue
			except KeyError:
				continue
		returnDict['H Name'] = nameSpriteDict['Home']['Proper']
		returnDict['H Sprite'] = nameSpriteDict['Home']['Sprite']
		returnDict['A Name'] = nameSpriteDict['Away']['Proper']
		returnDict['A Sprite'] = nameSpriteDict['Away']['Sprite']
		return returnDict
	else:
		originalWindow = driver.current_window_handle
		driver.find_element_by_id(matchDict['id']).click()
		wait.until(EC.number_of_windows_to_be(2))
		for window_handle in driver.window_handles:
			if window_handle != originalWindow:
				driver.switch_to.window(window_handle)
				break
		wait.until(EC.presence_of_element_located((By.LINK_TEXT, 'H2H'))) #Previously (By.ID, 'a-match-head-2-head')
		driver.find_element_by_link_text('H2H').click()
		wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'h2h___1pnzCTL'))) # Previously (By.CLASS_NAME, 'h2h-wrapper')
		h2hSoup = BeautifulSoup(driver.page_source, 'html.parser')
		h2hSoup = h2hSoup.find_all('div', class_='section___1a1N7yN')

		for side in list(nameSpriteDict.keys()):
			teamName = nameSpriteDict[side]['Name']
			for table in h2hSoup:
				table_title = table.find('div', class_='title___3_goVIi')
				if 'Head-to-head' in table_title.contents[0]:
					continue
				else:
					table_team = table.find('span', class_='highlighted___nwocTCH').contents[0]
					if table_team in nameSpriteDict[side]['Name']:
						if '(' in teamName:
							teamName = table_team
						h2hFlags = table.find_all('span', class_='flag___38-7xEI')
						h2hRegions =[]
						for flag in h2hFlags:
							flagTitle = flag['title']
							flagTitle = flagTitle[flagTitle.find('(')+1:flagTitle.find(')')]
							if flagTitle not in h2hRegions:
								h2hRegions.append(flagTitle)
						for region in h2hRegions:
							try:
								tNSDict[region][teamName]
								nameSpriteDict[side]['Proper'] = tNSDict[region][teamName]['Proper']
								nameSpriteDict[side]['Sprite'] = tNSDict[region][teamName]['Sprite']
								break		
							except KeyError:
								continue
					else:
						continue
		returnDict['H Name'] = nameSpriteDict['Home']['Proper']
		returnDict['H Sprite'] = nameSpriteDict['Home']['Sprite']
		returnDict['A Name'] = nameSpriteDict['Away']['Proper']
		returnDict['A Sprite'] = nameSpriteDict['Away']['Sprite']
		driver.close()
		driver.switch_to.window(originalWindow)
		return returnDict

def WTWTW():
	fs_round_translator = {'1/32-finals':'Round of 64','1/16-finals':'Round of 32', '1/8-finals':'Round of 16'}
	WTWTWmatches, competitionsDict = fetcher()
	WTWTWmatches = match_details(competitionsDict, WTWTWmatches)
	driver.quit()

	print("Writing listas.csv")
	with open('listas.csv', 'w', newline='', encoding='utf8') as listas:
		writer = csv.writer(listas, delimiter=';')
		for date in WTWTWmatches:
			for match in sorted(WTWTWmatches[date], key=lambda i: i['Time']):
				if match['Round'] in fs_round_translator:
					match['Round'] = fs_round_translator[match['Round']]
				writer.writerow([match['Time'], match['Home'], match['Away'], match['Competition'], match['Round']])
			writer.writerow([])
	print("Finished running WTWTW")
	return WTWTWmatches
"""
input('Press Enter to Continue...')
WTWTW()
"""
"""
Current state of WTWTWmatches dictionary:
WTWTWmatches = {
	day : [
		{
			'Time' : # timestamp,
			'id' : # game id used by FS,
			'Home' : # Home team,
			'Away' : # Away team,
			'Region' : # Region of match. Usually country (Portugal) or continent (Europe). Sometimes other (World, Australia & Oceania),
			'Competition' : # Name of competition,
			'Round' : # round name of match (Round of 32, Semi-finals, etc),
			'H Sprite' : # sprite for the home team,
			'A Sprite' : # sprite for the away team,
			'C Sprite' : # sprite for competition,
			'H FL Score' : # The match home team's score in the first leg,
			'A FL Score' : # The match away team's score in the first leg
		},
		{
			# repeat above dictionary for each match on this day
		}
	]
	next day : [
		# repeat for matches on the next day
	],
	# repeats for 7 days total
}

Current state of CompetitionsDict/competitions_dict
CompetitionsDict = {
	region1 : [competition1, competition2, etc],
	region2 : [competiton3, competition4, etc],
	etc
}
"""

"""
FUNCTION DESCRIPTIONS

WTWTW:
Main function.
Calls fetcher, calls match_details, quits chromedriver.
writes listas.csv one row at a time. The line with the lambda function ensures the listas file is written in chronological order

fetcher:
days variable is there to allow for troubleshooting. For example, programmer can easily change days to 1 if they want to focus on a specific day/match that is causing errors.
Creates the two dictionaries to eventually return.
For loop calls parser and clicks button on website for next day until complete.
time.sleep(2) is 2 second sleep. Shorter time, 1 second for example, sometimes created an issue where matches would be the same for multiple days.
	It seems that the parser function would be called and pull data before the website started to load the next day's data. 

parser:
Each time parser is called the website has a new day of the checked matches. It creates a list of the checked matches and what the date is to return.
The wait is there to allow the data to load. 'event__titleBox' was a div element that reloads each time the page loaded.
competitions_dict collects each of the competitions that are checked when WTWTW is run. Reason why is explained in match_details description.

match_details:


"""