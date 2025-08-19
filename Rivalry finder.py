from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup
import time
import csv
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


with open("Rivalries/rivalries.json", "r", encoding="utf8") as rf:
    rivalries = load(rf)


def check_json():
    countries = list(rivalries.keys())
    # Check countries are all caps
    is_all_uppercase = all(key.isupper() for key in countries)
    if is_all_uppercase:
        print("All countries are in uppercase")
    else:
        countries_in_lower_case = list(
            key for key in countries if not key.isupper()
        )
        print("Attention!! Countries in lower case:", countries_in_lower_case)

    # Check countries are in the right order
    if sorted(countries) == countries:
        pass
    else:
        print(
            "Attention!! Countries are not sorted in the correct order. Modify the file to this order:",
            sorted(countries),
        )
        for i in range(0, len(countries) - 1):
            if countries[i] > countries[i + 1]:
                print("Out of order country: ", countries[i])

    # Check if rivalries and teams are sorted

    for country in rivalries:
        countries_rivalries = rivalries[country]

        # Check if teams within each rivalry are sorted
        for i, rivalry in enumerate(countries_rivalries):
            if rivalry != sorted(rivalry):
                print(
                    f"Attention!! Teams in rivalry {rivalry} are not in alphabetical order"
                )

        # Check if rivalries are sorted
        if sorted(countries_rivalries) == countries_rivalries:
            pass
        else:
            print(
                "Attention!! Teams are not sorted in the correct order. Modify the file to this order:",
                sorted(countries_rivalries),
            )
            for i in range(0, len(countries_rivalries) - 1):
                if countries_rivalries[i] > countries_rivalries[i + 1]:
                    print("Out of order country: ", countries_rivalries[i])


def fetcher():
    days = 7
    print("Starting script ...")
    for n in range(days):
        daily_matches = matches_finder()
        matches_to_star = rivalries_finder(daily_matches)
        star_matches(matches_to_star)
        if n == (days - 1):
            print("Completed all days")
            return
        driver.find_element(
            By.CSS_SELECTOR,
            "button[data-day-picker-arrow='next']",  # Calendar button for next day
        ).click()
        time.sleep(5)


def matches_finder():
    matches = {}
    countries = list(rivalries.keys())
    wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "event__titleBox"))
    )
    soup = BeautifulSoup(driver.page_source, "html.parser")
    for country in countries:
        matches[country] = []
        try:
            league_section = soup.find(
                "span", class_="wclLeagueHeader__countryName", string=country
            ).find_parent("div", class_="wclLeagueHeader")
        except:  # In this case there are no matches for that country and the loop should continue
            continue
        current_match = league_section

        # While loop that checks if it's match or if it's a league header of the same country
        # It doesn't look the matches that are hidden
        while (
            # Check if it's league div element (it will be passed on the if statement)
            current_match
            and "wclLeagueHeader" in current_match.get("class")
            and current_match.find(
                "span", class_="wclLeagueHeader__countryName"
            ).get_text()
            == country
            # Check if it's an event match div element
        ) or (
            current_match
            and current_match.get("class")
            and "event__match" in current_match.get("class")
        ):
            if "wclLeagueHeader" in current_match.get("class"):
                pass
            else:
                temp = {}
                home_team = (
                    current_match.find("div", class_="event__homeParticipant")
                    .get_text()
                    .strip()
                )
                away_team = (
                    current_match.find("div", class_="event__awayParticipant")
                    .get_text()
                    .strip()
                )
                teams_tuple = tuple(sorted((home_team, away_team)))
                is_starred = (
                    current_match.find(
                        "button", {"data-testid": "wcl-favorite-active"}
                    )
                    is not None
                )  # Boolean

                temp["id"] = current_match["id"]
                temp["Home"] = home_team
                temp["Away"] = away_team
                temp["Teams"] = teams_tuple
                temp["star"] = is_starred

                matches[country].append(temp)

            current_match = current_match.find_next_sibling("div")
    return matches


def rivalries_finder(daily_matches):
    matches_to_star = []
    for country in daily_matches:
        if (
            len(daily_matches[country]) == 0
        ):  # Check if countries has no matches that day
            continue
        else:
            for fixture in daily_matches[country]:
                # print(fixture["Teams"])
                rivalaries_possibilities = set(
                    tuple(sorted(match))
                    for match in rivalries.get(country, [])
                )
                if fixture["Teams"] in rivalaries_possibilities:
                    matches_to_star.append(fixture)
                else:
                    pass
    return matches_to_star


def star_matches(matches_to_star):
    for fixture in matches_to_star:
        if fixture["star"]:
            pass
        else:
            print(fixture["Home"], "vs", fixture["Away"])
            driver.find_element(By.ID, fixture["id"]).find_element(
                By.CSS_SELECTOR, "button[data-testid='wcl-favorite-inactive']"
            ).click()


def debug_page_content():
    """Save the current page source to debug what's actually being loaded"""
    with open("debug_page_source.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    print("Page source saved to debug_page_source.html")


def debug_find_elements():
    """Check if the expected elements exist on the page"""
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Check for match containers
    event_titlebox = soup.find_all(class_="event__titleBox")
    print(f"Found {len(event_titlebox)} elements with class 'event__titleBox'")

    # Check for league headers
    league_headers = soup.find_all(
        "span", class_="wclLeagueHeader__countryName"
    )
    print(f"Found {len(league_headers)} league headers")

    if league_headers:
        print(
            "League header texts:",
            [header.get_text() for header in league_headers[:5]],
        )

    # Check for match events
    match_events = soup.find_all(class_="event__match")
    print(f"Found {len(match_events)} match events")

    # Check what countries are available
    countries_found = set()
    for header in league_headers:
        countries_found.add(header.get_text().strip())

    print("Countries found on page:", sorted(list(countries_found)))
    print("Countries in your rivalries JSON:", sorted(list(rivalries.keys())))


def matches_finder_debug():
    """Enhanced version with debugging"""
    matches = {}
    countries = list(rivalries.keys())

    # Add explicit wait and debugging
    try:
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "event__titleBox"))
        )
        print("✓ Found event__titleBox elements")
    except:
        print("✗ Could not find event__titleBox elements")
        # Try alternative selectors
        alternative_selectors = ["event__match", "match", "fixture", "game"]
        for selector in alternative_selectors:
            elements = driver.find_elements(By.CLASS_NAME, selector)
            if elements:
                print(
                    f"Found {len(elements)} elements with class '{selector}'"
                )

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Debug the parsing
    debug_find_elements()

    for country in countries:
        matches[country] = []
        print(f"\nLooking for matches in: {country}")

        try:
            league_section = soup.find(
                "span", class_="wclLeagueHeader__countryName", string=country
            ).find_parent("div", class_="wclLeagueHeader")
            print(f"✓ Found league section for {country}")
        except Exception as e:
            print(f"✗ Could not find league section for {country}: {e}")
            continue

        # Continue with your existing logic but add more debugging
        current_match = league_section
        match_count = 0

        while (
            current_match
            and "wclLeagueHeader" in current_match.get("class", [])
            and current_match.find(
                "span", class_="wclLeagueHeader__countryName"
            ).get_text()
            == country
        ) or (
            current_match
            and current_match.get("class")
            and "event__match" in current_match.get("class", [])
        ):
            if "wclLeagueHeader" in current_match.get("class", []):
                print(
                    f"  Found league header: {current_match.find('span', class_='wclLeagueHeader__countryName').get_text()}"
                )
            else:
                match_count += 1
                try:
                    temp = {}
                    home_team = (
                        current_match.find(
                            "div", class_="event__homeParticipant"
                        )
                        .get_text()
                        .strip()
                    )
                    away_team = (
                        current_match.find(
                            "div", class_="event__awayParticipant"
                        )
                        .get_text()
                        .strip()
                    )
                    print(f"  Match {match_count}: {home_team} vs {away_team}")

                    teams_tuple = tuple(sorted((home_team, away_team)))
                    is_starred = (
                        current_match.find(
                            "button", {"data-testid": "wcl-favorite-active"}
                        )
                        is not None
                    )

                    temp["id"] = current_match["id"]
                    temp["Home"] = home_team
                    temp["Away"] = away_team
                    temp["Teams"] = teams_tuple
                    temp["star"] = is_starred

                    matches[country].append(temp)

                except Exception as e:
                    print(f"  ✗ Error parsing match: {e}")

            current_match = current_match.find_next_sibling("div")

        print(f"Found {len(matches[country])} matches for {country}")

    return matches


# Replace your fetcher function with this debug version
def fetcher_debug():
    days = 7
    print("Starting script ...")

    # Debug the first day thoroughly
    print("\n=== DEBUGGING FIRST DAY ===")
    debug_page_content()
    daily_matches = matches_finder_debug()

    print(
        f"\nTotal matches found: {sum(len(matches) for matches in daily_matches.values())}"
    )

    matches_to_star = rivalries_finder(daily_matches)
    print(f"Rivalry matches to star: {len(matches_to_star)}")

    for match in matches_to_star:
        print(f"  - {match['Home']} vs {match['Away']}")

    # Ask user if they want to continue with all days
    continue_all = input("Continue with all 7 days? (y/n): ").lower() == "y"

    if not continue_all:
        return

    # Continue with remaining days (less verbose)
    for n in range(1, days):
        daily_matches = matches_finder()
        matches_to_star = rivalries_finder(daily_matches)
        star_matches(matches_to_star)
        if n == (days - 1):
            print("Completed all days")
            return
        driver.find_element(
            By.CSS_SELECTOR,
            "button[data-day-picker-arrow='next']",
        ).click()
        time.sleep(5)


input("Press Enter to Continue...")
fetcher()
driver.close()
