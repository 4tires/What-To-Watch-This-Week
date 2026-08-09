from selenium import webdriver
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
    TimeoutException,
)
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
from enum import Enum
import WTWTW_Post
import pyperclip
from dataclasses import dataclass
from typing import Optional

### SELENIUM INITIATION

URL = "https://www.flashscore.com/"

options = webdriver.FirefoxOptions()
options.add_argument("--ignore-certificate-errors")
options.add_argument("--ignore-ssl-errors")
options.set_capability("unhandledPromptBehavior", "dismiss")

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
    print("Login finished")
time.sleep(3)
username = driver.find_element(By.ID, "email")
username.clear()
username.send_keys(username_credential)

password = driver.find_element(By.NAME, "password")
password.clear()
password.send_keys(password_credential)
driver.find_element(By.CLASS_NAME, "wcl-button_eGaDi").click()

### CLASS DEFINING AND DICTIONARIES


@dataclass
class Match:
    time: str
    match_id: str
    home: str
    away: str
    region: str
    competition: str
    round_name: Optional[str] = None
    home_sprite: Optional[str] = None
    away_sprite: Optional[str] = None
    competition_sprite: Optional[str] = None
    home_fl_score: Optional[str] = None
    away_fl_score: Optional[str] = None


# These round keywords will trigger opening the link of each match that belongs to a competition with the following text, so that we can fetch the round
ROUND_KEYWORDS = [
    "qualification",
    "play offs",
    "play-offs",
    "relegation",
    "promotion",
    "copa",
    "cup",
]

### SELENIUM FETCHING


def WTWTW():
    global wtwtw_matches  # REMOVE
    fetcher()
    match_details()
    driver.quit()
    wtwtw_matches = WTWTW_Post.WTWTW_bold_prompt(wtwtw_matches)
    print("Writing Reddit post.")
    WTWTW_Post.WTWTW_post_writer(wtwtw_matches)
    print("Completed.")
    with open(
        r"C:\Users\paulo\OneDrive\Documentos\Programação\Projectos\What To Watch This Week\What-To-Watch-This-Week\WTWTW_post.txt",
        "r",
        encoding="utf-8",
    ) as f:
        pyperclip.copy(f.read())
    print("Finished running WTWTW")
    return


def fetcher():
    global wtwtw_matches  # REMOVE
    days = 7
    for n in range(days):
        date, checked_matches = parser()
        wtwtw_matches[date] = checked_matches
        if n == (days - 1):
            print("Completed all parsers")
            return
        driver.find_element(
            By.CSS_SELECTOR, "button[data-day-picker-arrow='next']"
        ).click()
        time.sleep(5)


def get_competition_for_match(match_div, soup):
    # Walk backwards through all preceding elements to find nearest league header
    header = match_div.find_previous("a", class_="headerLeague__title")
    if header is None:
        raise RuntimeError(
            f"No competition header found for match {match_div.get('id')}"
        )
    return header.get_text(strip=True)


def needs_round_fetch(competition_name: str) -> bool:
    name_lower = competition_name.lower()
    return any(keyword in name_lower for keyword in ROUND_KEYWORDS)


def fetch_competition_with_round(match_div, main_window):
    link_el = match_div.find("a", class_="eventRowLink")
    if link_el is None or not link_el.get("href"):
        raise RuntimeError(
            f"No detail link found for match {match_div.get('id')}"
        )

    detail_url = link_el["href"]

    driver.execute_script("window.open(arguments[0]);", detail_url)
    driver.switch_to.window(driver.window_handles[-1])

    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, '[data-testid="wcl-breadcrumbsItem"]')
        )
    )
    detail_soup = BeautifulSoup(driver.page_source, "html.parser")

    breadcrumb_items = detail_soup.select(
        'li[data-testid="wcl-breadcrumbsItem"] span[data-testid="wcl-scores-overline-03"]'
    )
    if not breadcrumb_items:
        raise RuntimeError(
            f"No breadcrumb found on match detail page: {detail_url}"
        )

    competition_name = breadcrumb_items[-1].get_text(strip=True)

    driver.close()
    driver.switch_to.window(main_window)

    return competition_name


def get_favourite_matches():
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "event__match")))
    soup = BeautifulSoup(driver.page_source, "html.parser")

    date_el = soup.find("button", attrs={"data-testid": "wcl-dayPickerButton"})
    date = date_el.get("aria-label") if date_el else None

    star_buttons = soup.find_all(
        "button",
        attrs={"data-testid": "wcl-favorite-active"},
        class_="eventSubscriber__star--event",
    )

    list_of_matches = [
        btn.find_parent("div", class_="event__match") for btn in star_buttons
    ]

    """
    To debug the next error in case any star match doesn't have a parent':
        for i, btn in enumerate(star_buttons):
            parent = btn.find_parent("div", class_="event__match")
            if parent is None:
                print(f"Button #{i} failed. HTML context:")
                print(btn.prettify())
                print(btn.find_parent("div"))
    """

    if any(m is None for m in list_of_matches):
        raise RuntimeError(
            "A favorited star button had no event__match ancestor — page structure may have changed."
        )

    # Get the competition
    main_window = driver.current_window_handle

    for match_div in list_of_matches:
        competition_name = get_competition_for_match(match_div, soup)

        if needs_round_fetch(competition_name):
            competition_name = fetch_competition_with_round(
                match_div, main_window
            )

        match_div["data-competition-name"] = competition_name

    return date, list_of_matches


# TRANSFORMATION LOGIC
def parser():
    checked_matches = get_favourite_matches()

    for match_ in list_of_matches:
        temp = {}
        try:
            time = (
                match_.find("div", class_="event__time")
                .get_text()
                .replace(":", "")
                .replace("FRO", "")
            )
        except:
            time = "No time"
        home_team = match_.find(
            "div", class_="event__homeParticipant"
        ).get_text()
        away_team = match_.find(
            "div", class_="event__awayParticipant"
        ).get_text()
        competition = (
            match_.find_previous_sibling("div", class_="headerLeague__wrapper")
            .find("div", class_="headerLeague__body")
            .find("a")
            .get_text()
        )
        region = (
            match_.find_previous_sibling("div", class_="headerLeague__wrapper")
            .find("span", class_="headerLeague__category-text")
            .get_text()
        )
        if region in competitions_dict:
            if competition in competitions_dict[region]:
                pass
            else:
                competitions_dict[region].append(competition)
        else:
            competitions_dict[region] = [competition]
        temp["Time"] = time
        temp["id"] = match_["id"]
        temp["Home"] = home_team
        temp["Away"] = away_team
        temp["Region"] = region
        temp["Competition"] = competition
        checked_matches.append(temp)
    print("Completed day")
    return date, checked_matches


def match_details():
    print("Fetching match round and aggregate score.")
    fs_round_translator = {
        "1/32-finals": "Round of 64",
        "1/16-finals": "Round of 32",
        "1/8-finals": "Round of 16",
    }
    global wtwtw_matches, competitions_dict
    continent_list = [
        "Asia",
        "Africa",
        "Europe",
        "North & Central America",
        "South America",
        "Australia & Oceania",
        "World",
    ]
    with open(
        "./TeamNames-Sprites/CompNames-Sprites.json", "r", encoding="utf8"
    ) as rf:
        competition_sprite_json = load(rf)
    with open("FSJSON/fslinks.json", "r") as fs:
        fs_json = load(fs)
    for region in competitions_dict:
        for competition in competitions_dict[region]:
            league_type = League_Type.LEAGUE
            href = None
            (
                competition_proper,
                region_proper,
            ) = competition_and_region_proper_names(
                competition, region, fs_json
            )
            if competition_proper in list(
                fs_json["Competitions"][region_proper].keys()
            ):
                href = fs_json["Competitions"][region_proper][
                    competition_proper
                ]
            gamelist = competition_matches(href) if href != None else None
            for date in wtwtw_matches:
                for match_ in wtwtw_matches[date]:
                    if (
                        match_["Region"] == region
                        and match_["Competition"] == competition
                    ):
                        if "Qualification" in competition:
                            round = "Qualification"
                        elif gamelist != None:
                            round = find_round(
                                match_["Home"], match_["Away"], gamelist
                            )
                        else:
                            round = None
                        match_["Round"] = round
                        if round != None:
                            league_type = League_Type.CUP
            if (
                league_type == League_Type.CUP
                and "Super Cup" not in competition
            ):
                try:
                    driver.get(URL + href + "results")
                    wait.until(
                        EC.presence_of_element_located(
                            (
                                By.XPATH,
                                "//div[contains(@class,'event__match') or contains(@class, 'event__homeParticipant')]",
                            )
                        )
                    )
                    for date in wtwtw_matches:
                        for match_ in wtwtw_matches[date]:
                            if (
                                match_["Region"] == region
                                and match_["Competition"] == competition
                            ):
                                if match_["Round"] != None:
                                    aggregate = find_aggregate(
                                        match_["Home"],
                                        match_["Away"],
                                        match_["Round"],
                                    )
                                    match_["H FL Score"] = aggregate[1]
                                    match_["A FL Score"] = aggregate[0]
                                    if match_["Round"] in fs_round_translator:
                                        match_["Round"] = fs_round_translator[
                                            match_["Round"]
                                        ]
                except:
                    print(
                        "Error: Results page not found or other error in retrieving round info and aggregate score in ",
                        competition,
                    )
                driver.get(URL + href + "fixtures")
                wait.until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "event__homeParticipant")
                    )
                )
            for date in wtwtw_matches:
                for match_ in wtwtw_matches[date]:
                    if (
                        match_["Region"] == region
                        and match_["Competition"] == competition
                    ):
                        match_["Region"] = region_proper
                        match_["Competition"] = competition_proper
                        if competition_proper in list(
                            competition_sprite_json[region_proper].keys()
                        ):
                            match_["C Sprite"] = competition_sprite_json[
                                region_proper
                            ][competition_proper]["Sprite"]
                            temp_comp_proper = competition_sprite_json[
                                region_proper
                            ][competition_proper]["Proper"]
                            match_["Competition"] = (
                                temp_comp_proper
                                if temp_comp_proper != None
                                else competition_proper
                            )
                        else:
                            match_["C Sprite"] = None
                        if region_proper in continent_list:
                            name_sprite_dict = find_name_and_sprite(
                                match_, Competition_Type.INTERNATIONAL
                            )
                        else:
                            name_sprite_dict = find_name_and_sprite(
                                match_, Competition_Type.DOMESTIC
                            )
                        if (round == None) and (
                            name_sprite_dict["Group"] != None
                        ):
                            match_["Round"] = name_sprite_dict["Group"]
                        match_["Home"] = (
                            name_sprite_dict["H Name"]
                            if name_sprite_dict["H Name"] != None
                            else match_["Home"]
                        )
                        match_["Away"] = (
                            name_sprite_dict["A Name"]
                            if name_sprite_dict["A Name"] != None
                            else match_["Away"]
                        )
                        for side in ["Home", "Away"]:
                            if (
                                " (" in match_[side]
                                and " (Am)" not in match_[side]
                            ):
                                match_[side] = match_[side][
                                    0 : match_[side].find(" (")
                                ]
                        match_["H Sprite"] = name_sprite_dict["H Sprite"]
                        match_["A Sprite"] = name_sprite_dict["A Sprite"]


def competition_and_region_proper_names(competition, region, fs_json_file):
    for key in fs_json_file["Competitions"]:
        if region.lower() == key.lower():
            region = key
            break
    if competition in list(fs_json_file["Competitions"][region].keys()):
        return competition, region
    elif "-" in competition:
        competition_name_split = competition.split(" - ")
        for n in range(len(competition_name_split)):
            competition_temp = " - ".join(competition_name_split[: n + 1])
            if competition_temp in list(
                fs_json_file["Competitions"][region].keys()
            ):
                return competition_temp, region
        print(
            "Error: No matching competition found for ",
            competition,
            " in ",
            region,
        )
        return competition, region
    else:
        print(
            "Error: No matching competition found for ",
            competition,
            " in ",
            region,
        )
        return competition, region


def competition_matches(href):
    checked_matches_list = []

    driver.get(URL + href + "fixtures")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    checked_matches_star = soup.find_all(
        "svg", attrs={"data-testid": "wcl-icon-action-state-favorite-active"}
    )
    for match_ in checked_matches_star:
        checked_matches_list.append(
            match_.find_parent("div", class_="event__match")
        )
    checked_matches_list = list(filter(None, checked_matches_list))
    return checked_matches_list


def find_round(home, away, gamelist):
    # fs_round_translator = {'1/32-finals':'Round of 64','1/16-finals':'Round of 32', '1/8-finals':'Round of 16'}
    round = None
    for item in gamelist:
        home_team = item.find(
            "div", class_="event__homeParticipant"
        ).get_text()
        away_team = item.find(
            "div", class_="event__awayParticipant"
        ).get_text()
        if home_team == home and away_team == away:
            # Line 198 makes this unnecessary, but if it doesn't work for everything, might be usefull to use code below
            # superior_round = item.find_previous_sibling("div", class_="event__header").get_text()
            # if "Qualification" in superior_round:
            #     round = "Qualification"
            #     return round
            round = item.find_previous_sibling("div", class_="event__round")
            round = round.get_text() if round != None else None
            if round != None:
                if "Round " in round[:6] and len(round) in [7, 8]:
                    round = None
            return round
    print("No results for " + home + " vs " + away + " round.")
    return round


def find_aggregate(second_leg_home_team, second_leg_away_team, round_name):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    table_round_header = soup.find("div", string=round_name)
    first_leg_score_home = None
    first_leg_score_away = None
    if table_round_header != None:
        row = table_round_header
        while True:
            row = row.next_sibling
            if row == None:
                break
            elif any(
                item in ["event__round", "wclLeagueHeader"]
                for item in row["class"]
            ):
                break
            else:
                try:
                    first_leg_home_team = row.find(
                        "div", class_="event__homeParticipant"
                    ).get_text()
                except:
                    break
                first_leg_away_team = row.find(
                    "div", class_="event__awayParticipant"
                ).get_text()
                if (first_leg_home_team == second_leg_away_team) and (
                    first_leg_away_team == second_leg_home_team
                ):
                    # first_leg_score = row.find('div', class_='event__scores').find_all('span')
                    first_leg_score_home = row.find(
                        "div", class_="event__score--home"
                    ).get_text()
                    first_leg_score_away = row.find(
                        "div", class_="event__score--away"
                    ).get_text()
                    break
    return [first_leg_score_home, first_leg_score_away]


def find_name_and_sprite(match_dict, competition_type):
    region = match_dict["Region"]
    name_and_sprite_Dict = {}
    name_and_sprite_Dict["Home"] = {
        "Name": match_dict["Home"],
        "Proper": None,
        "Sprite": None,
        "h2h": "h2h_home",
    }
    name_and_sprite_Dict["Away"] = {
        "Name": match_dict["Away"],
        "Proper": None,
        "Sprite": None,
        "h2h": "h2h_away",
    }
    return_dict = {
        "H Name": None,
        "H Sprite": None,
        "A Name": None,
        "A Sprite": None,
        "Group": None,
    }

    with open(
        "./TeamNames-Sprites/TeamNames-Sprites-V2.json", "r", encoding="utf8"
    ) as rf:
        team_name_and_sprite_dict = load(rf)
    if competition_type == Competition_Type.DOMESTIC:
        for side in list(name_and_sprite_Dict.keys()):
            team_name = name_and_sprite_Dict[side]["Name"]
            try:
                team_name_and_sprite_dict[region][team_name]
                name_and_sprite_Dict[side]["Proper"] = (
                    team_name_and_sprite_dict[region][team_name]["Proper"]
                )
                name_and_sprite_Dict[side]["Sprite"] = (
                    team_name_and_sprite_dict[region][team_name]["Sprite"]
                )
                continue
            except KeyError:
                print("Error: Unable to find sprite for " + team_name)
                continue
        return_dict["H Name"] = name_and_sprite_Dict["Home"]["Proper"]
        return_dict["H Sprite"] = name_and_sprite_Dict["Home"]["Sprite"]
        return_dict["A Name"] = name_and_sprite_Dict["Away"]["Proper"]
        return_dict["A Sprite"] = name_and_sprite_Dict["Away"]["Sprite"]
        return return_dict
    else:
        original_window = driver.current_window_handle
        temp_match_link = (
            driver.find_element(By.ID, match_dict["id"])
            .find_element(By.CLASS_NAME, "eventRowLink")
            .get_attribute("href")
        )
        driver.switch_to.new_window("window")
        driver.get(temp_match_link)
        wait.until(EC.number_of_windows_to_be(2))
        for window_handle in driver.window_handles:
            if window_handle != original_window:
                driver.switch_to.window(window_handle)
                break
        wait.until(EC.presence_of_element_located((By.LINK_TEXT, "H2H")))
        driver.find_element(By.LINK_TEXT, "H2H").click()
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "h2h__participant"))
        )
        h2h_soup = BeautifulSoup(driver.page_source, "html.parser")
        h2h_section = h2h_soup.find_all("div", class_="h2h__section")

        for side in list(name_and_sprite_Dict.keys()):
            team_name = name_and_sprite_Dict[side]["Name"]
            # Euros and Copa America share the same header region as Champions League, Libertadores, etc.
            # Best to check these competitions here and skip code to region
            # Take into account that below the flag title doesn't add to h2h_regions if it's Europe or South America
            competition = (
                h2h_soup.find("a", class_="wcl-breadcrumbItemLabel_2QT1M")
                .find("span")
                .text.rsplit(" -", -1)[0]
            )
            h2h_regions = []

            if competition == "Euro":
                h2h_regions = ["Europe"]
            elif competition == "Copa América":
                h2h_regions = ["South America", "North & Central America"]
            else:
                # Team name must know if there is (Country) in team name
                # South American competitions have always, example: Millonarios (Col)
                if "(" in team_name:
                    team_name = team_name[: team_name.find("(") - 1]
                for table in h2h_section:
                    table_title = table.find("div")
                    if team_name in table_title.get_text():
                        h2h_flags = table.find_all("span", class_="h2h__flag")
                        h2h_regions = []
                        for flag in h2h_flags:
                            flag_title = flag.find("span").get("title")
                            flag_title = flag_title[
                                flag_title.find("(") + 1 : flag_title.find(")")
                            ]
                            if (
                                flag_title not in h2h_regions
                                and flag_title
                                not in [
                                    "Europe",
                                    "South America",
                                ]
                            ):
                                h2h_regions.append(flag_title)
            for region in h2h_regions:
                if region == "World":
                    region = flag_title
                else:
                    try:
                        team_name_and_sprite_dict[region][team_name]
                        name_and_sprite_Dict[side]["Proper"] = (
                            team_name_and_sprite_dict[region][team_name][
                                "Proper"
                            ]
                        )
                        name_and_sprite_Dict[side]["Sprite"] = (
                            team_name_and_sprite_dict[region][team_name][
                                "Sprite"
                            ]
                        )
                        break
                    except KeyError:
                        print("Error: Unable to find sprite for " + team_name)
                        continue
        return_dict["H Name"] = name_and_sprite_Dict["Home"]["Proper"]
        return_dict["H Sprite"] = name_and_sprite_Dict["Home"]["Sprite"]
        return_dict["A Name"] = name_and_sprite_Dict["Away"]["Proper"]
        return_dict["A Sprite"] = name_and_sprite_Dict["Away"]["Sprite"]

        tabs = h2h_soup.find_all("button", attrs={"role": "tab"})
        for tab in tabs:
            if tab.contents[0] != "Standings":
                continue
            else:
                try:
                    driver.find_element(By.LINK_TEXT, "STANDINGS").click()
                    wait.until(
                        EC.presence_of_element_located(
                            (By.CLASS_NAME, "tableWrapper")
                        )
                    )
                except:
                    print("Error: Unable to find table in Standings tab.")
                    break
                h2h_soup = BeautifulSoup(driver.page_source, "html.parser")
                standing_tables = h2h_soup.find_all(
                    "div", class_="table__headerCell--participant"
                )
                for table in standing_tables:
                    table_header = table.contents[0]
                    if "Group " in table_header:
                        return_dict["Group"] = table_header
                        break
                    else:
                        continue
        driver.close()
        driver.switch_to.window(original_window)
        return return_dict


input("Press Enter to Continue...")
WTWTW()

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

wtwtw_matches and competition_dict are global variables initiated outside of functions

WTWTW:
Main function.
Calls fetcher, calls match_details, quits chromedriver.
Commented out: Writes listas.csv one row at a time. The line with the lambda function ensures the listas file is written in chronological order

fetcher:
Days variable is there to allow for troubleshooting. For example, programmer can easily change days to 1 if they want to focus on a specific day/match that is causing errors.
For loop calls parser and clicks button on website for next day until complete.
time.sleep(2) is 2 second sleep. Shorter time, 1 second for example, sometimes created an issue where matches would be the same for multiple days.
    - It seems that the parser function is called and pulls data before the website started to load the next day's data. 

parser:
Each time parser is called the website has a new day of the checked matches. It creates a list of the checked matches and what the date is to return.
The wait is there to allow the data to load. 'event__titleBox' was a div element that reloads each time the page loaded.
competitions_dict collects each of the competitions that are checked when WTWTW is run. More in match_details description.

match_details:
This function starts off by reading a dictionary file with competition names and sprites and anothe with links to the website.
The competitions_dict dictionary is used to iterate through each competition. The goal is to make changes to all of the matches from the same competition in wtwtw_matches.
This should reduce the run time since there should be less competitions in wtwtw_matches than total matches.
The function finds each competition website link, grabs relevant data for all the matches, and updates wtwtw_matches.
If the match is a cup it then searches for a first leg score.
Afterwards it iterates through wtwtw_matches again to update match details such as competition name or team name as well as add the sprite

competition_and_region_proper_names:
Tries to find the proper name of the competition and region. Sometimes the competition name on the website has additional information (such as " - Playoffs")

competition_matches: 
takes href input and returns list of all the starred matches.

find_round:
searches list for match, and returns the round name of the match.

find_aggregate:
searches page for first leg game (where home team was away and vice versa)
returns array with scores

find_name_and_sprite:
Creates name_and_sprite_dict for easy iterating.
Searches through json file with proper team names and sprites of team logo



"""
