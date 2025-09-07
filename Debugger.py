from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup
import time
from login_credentials import (
    username_credential,
    password_credential,
    chromedriver_path,
)
from json import load

URL = "https://www.flashscore.com/"

options = webdriver.FirefoxOptions()
options.add_argument("--ignore-certificate-errors")
options.add_argument("--ignore-ssl-errors")

service = Service(executable_path=chromedriver_path)
driver = webdriver.Firefox(service=service, options=options)
driver.implicitly_wait(30)
driver.get(URL)
wait = WebDriverWait(driver, 10)

driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
driver.find_element(By.ID, "user-menu").click()
driver.find_element(By.CLASS_NAME, "email").click()


try:
    element = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "lsidDialog"))
    )
finally:
    print("Login")
time.sleep(3)
username = driver.find_element(By.ID, "email")
username.clear()
username.send_keys(username_credential)

password = driver.find_element(By.NAME, "password")
password.clear()
password.send_keys(password_credential)
driver.find_element(By.CLASS_NAME, "wcl-button_eGaDi").click()


def debug_find_elements():
    """Check if the expected elements exist on the page"""
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Date
    if soup.find("button", class_="wcl-button_mrGAO") is None:
        print("Invalid Date")

    if soup.find("button", {"data-day-picker-arrow": "next"}) is None:
        print("Invalid next day arrow")

    # Check for a match with a star
    if (
        soup.find("button", attrs={"data-testid": "wcl-favorite-active"})
        is None
    ):
        print("No match with a star was found")


def fetcher_debug():
    print("Debugging elements on front page")
    debug_find_elements()
    pass


input("Press Enter to Continue...")
fetcher_debug()
