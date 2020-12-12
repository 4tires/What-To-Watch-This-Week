from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
from login_credentials import username_credential, password_credential


url = "https://www.flashscore.com/"

options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')

driver = webdriver.Chrome(executable_path='C:\\Users\micha\Documents\VSCode\What-To-Watch-This-Week\chromedriver.exe', chrome_options=options)
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
time.sleep(10)

competitioncount = {}

def parser():
	soup = BeautifulSoup(driver.page_source, 'html.parser')
	date = soup.find('div', class_='calendar__datepicker').get_text().split(' ')[0].replace('/', '.')
	matches = soup.find_all('div', class_='checked')
	list_of_matches = []
	for match in matches:
		list_of_matches.append(match.find_parent('div', class_='event__match'))
	list_matches = list(filter(None, list_of_matches))

	with open ('listas.csv', 'a', newline='') as listas:
		writer = csv.writer(listas, delimiter = ";")

		for match in list_matches:
			try:
				time = match.find('div', class_='event__time').get_text().replace(":", "")
			except:
				time = "No time"
			home_team = match.find('div', class_='event__participant--home').get_text()
			away_team = match.find('div', class_='event__participant--away').get_text()
			competition = match.find_previous_sibling('div', class_ = "event__header").find('span', class_ = "event__title--name").get_text()
			country = match.find_previous_sibling('div', class_ = "event__header").find('span', class_ = "event__title--type").get_text()
			if (country in competitioncount):
				if (competition in competitioncount[country]):
					competitioncount[country][competition] += 1
				else:
					competitioncount[country][competition] = 1
			else:
				competitioncount[country] = {competition: 1}
			writer.writerow([date, time, home_team, away_team, country, competition])
		writer.writerow([])
        
	print("Completed day")

def fetcher():
	parser()
	driver.find_element_by_class_name('calendar__direction--tomorrow').click()
	time.sleep(2)
	parser()
	"""
	driver.find_element_by_class_name('calendar__direction--tomorrow').click()
	time.sleep(2)
	parser()
	driver.find_element_by_class_name('calendar__direction--tomorrow').click()
	time.sleep(2)
	parser()
	driver.find_element_by_class_name('calendar__direction--tomorrow').click()
	time.sleep(2)
	parser()
	driver.find_element_by_class_name('calendar__direction--tomorrow').click()
	time.sleep(3)
	parser()
	driver.find_element_by_class_name('calendar__direction--tomorrow').click()
	time.sleep(3)
	parser()
	print("Completed all parsers")
	"""
fetcher()
print(competitioncount)