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
from enum import Enum
import WTWTW_Post
import pyperclip


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
driver.find_element(By.CLASS_NAME, "lsidDialog__button").click()

competitions_dict = {}
wtwtw_matches = {}


class Competition_Type(Enum):
    DOMESTIC = 0
    INTERNATIONAL = 1


class League_Type(Enum):
    CUP = 0
    LEAGUE = 1


def WTWTW():
    global wtwtw_matches
    fetcher()
    match_details()
    driver.quit()
    """
    print("Writing listas.csv")
    with open('listas.csv', 'w', newline='', encoding='utf8') as listas:
        writer = csv.writer(listas, delimiter=';')
        for date in wtwtw_matches:
            for match in sorted(wtwtw_matches[date], key=lambda i: i['Time']):
                if match['Round'] in fs_round_translator:
                    match['Round'] = fs_round_translator[match['Round']]
                writer.writerow([match['Time'], match['Home'], match['Away'], match['Competition'], match['Round']])
            writer.writerow([])
    """
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
    global wtwtw_matches
    days = 7
    for n in range(days):
        date, checked_matches = parser()
        wtwtw_matches[date] = checked_matches
        if n == (days - 1):
            print("Completed all parsers")
            return
        driver.find_element(
            By.CLASS_NAME, "calendar__navigation--tomorrow"
        ).click()
        time.sleep(5)


def parser():
    global competition_dict
    checked_matches = []

    wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, "event__titleBox"))
    )
    soup = BeautifulSoup(driver.page_source, "html.parser")
    date = soup.find("button", class_="calendar__datepicker").get_text()
    matches = soup.find_all("svg", class_="eventStar--active")

    list_of_matches = []
    for match in matches:
        list_of_matches.append(match.find_parent("div", class_="event__match"))
    list_of_matches = list(filter(None, list_of_matches))
    for match in list_of_matches:
        temp = {}
        try:
            time = (
                match.find("div", class_="event__time")
                .get_text()
                .replace(":", "")
                .replace("FRO", "")
            )
        except:
            time = "No time"
        home_team = match.find(
            "div", class_="event__homeParticipant"
        ).get_text()
        away_team = match.find(
            "div", class_="event__awayParticipant"
        ).get_text()
        competition = (
            match.find_previous_sibling("div", class_="wclLeagueHeader")
            .find("a", class_="wclLeagueHeader__textColor")
            .get_text()
        )
        region = (
            match.find_previous_sibling("div", class_="wclLeagueHeader")
            .find("span", class_="wclLeagueHeader__textColor")
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
        temp["id"] = match["id"]
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
                for match in wtwtw_matches[date]:
                    if (
                        match["Region"] == region
                        and match["Competition"] == competition
                    ):
                        if "Qualification" in competition:
                            round = "Qualification"
                        elif gamelist != None:
                            round = find_round(
                                match["Home"], match["Away"], gamelist
                            )
                        else:
                            round = None
                        match["Round"] = round
                        if round != None:
                            league_type = League_Type.CUP
            if league_type == League_Type.CUP:
                try:
                    driver.get(URL + href + "results")
                    wait.until(
                        EC.presence_of_element_located(
                            (
                                By.XPATH,
                                "//div[contains(@class,'event__titleBox') or contains(@class, 'event__homeParticipant')]",
                            )
                        )
                    )
                    for date in wtwtw_matches:
                        for match in wtwtw_matches[date]:
                            if (
                                match["Region"] == region
                                and match["Competition"] == competition
                            ):
                                if match["Round"] != None:
                                    aggregate = find_aggregate(
                                        match["Home"],
                                        match["Away"],
                                        match["Round"],
                                    )
                                    match["H FL Score"] = aggregate[1]
                                    match["A FL Score"] = aggregate[0]
                                    if match["Round"] in fs_round_translator:
                                        match["Round"] = fs_round_translator[
                                            match["Round"]
                                        ]
                except NameError as error:
                    print(
                        "Error: Results page not found or other error in retrieving round info and aggregate score"
                    )
                driver.get(URL + href + "fixtures")
                wait.until(
                    EC.presence_of_element_located(
                        (By.CLASS_NAME, "event__homeParticipant")
                    )
                )
            for date in wtwtw_matches:
                for match in wtwtw_matches[date]:
                    if (
                        match["Region"] == region
                        and match["Competition"] == competition
                    ):
                        match["Region"] = region_proper
                        match["Competition"] = competition_proper
                        if competition_proper in list(
                            competition_sprite_json[region_proper].keys()
                        ):
                            match["C Sprite"] = competition_sprite_json[
                                region_proper
                            ][competition_proper]["Sprite"]
                            temp_comp_proper = competition_sprite_json[
                                region_proper
                            ][competition_proper]["Proper"]
                            match["Competition"] = (
                                temp_comp_proper
                                if temp_comp_proper != None
                                else competition_proper
                            )
                        else:
                            match["C Sprite"] = None
                        if region_proper in continent_list:
                            name_sprite_dict = find_name_and_sprite(
                                match, Competition_Type.INTERNATIONAL
                            )
                        else:
                            name_sprite_dict = find_name_and_sprite(
                                match, Competition_Type.DOMESTIC
                            )
                        if (round == None) and (
                            name_sprite_dict["Group"] != None
                        ):
                            match["Round"] = name_sprite_dict["Group"]
                        match["Home"] = (
                            name_sprite_dict["H Name"]
                            if name_sprite_dict["H Name"] != None
                            else match["Home"]
                        )
                        match["Away"] = (
                            name_sprite_dict["A Name"]
                            if name_sprite_dict["A Name"] != None
                            else match["Away"]
                        )
                        for side in ["Home", "Away"]:
                            if (
                                " (" in match[side]
                                and " (Am)" not in match[side]
                            ):
                                match[side] = match[side][
                                    0 : match[side].find(" (")
                                ]
                        match["H Sprite"] = name_sprite_dict["H Sprite"]
                        match["A Sprite"] = name_sprite_dict["A Sprite"]


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
    checked_matches_star = soup.find_all("svg", class_="eventStar--active")
    for match in checked_matches_star:
        checked_matches_list.append(
            match.find_parent("div", class_="event__match")
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
        driver.find_element(By.ID, match_dict["id"]).click()
        wait.until(EC.number_of_windows_to_be(2))
        for window_handle in driver.window_handles:
            if window_handle != original_window:
                driver.switch_to.window(window_handle)
                break
        wait.until(EC.presence_of_element_located((By.LINK_TEXT, "H2H")))
        driver.find_element(By.LINK_TEXT, "H2H").click()
        wait.until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "h2h__participantInner")
            )
        )
        h2h_soup = BeautifulSoup(driver.page_source, "html.parser")
        h2h_section = h2h_soup.find_all("div", class_="h2h__section")

        for side in list(name_and_sprite_Dict.keys()):
            team_name = name_and_sprite_Dict[side]["Name"]
            # Euros and Copa America share the same header region as Champions League, Libertadores, etc.
            # Best to check these competitions here and skip code to region
            # Take into account that below the flag title doesn't add to h2h_regions if it's Europe or South America
            competition = (
                h2h_soup.find("span", class_="tournamentHeader__country")
                .find("a")
                .text.rsplit(" -", 1)[0]
            )
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
                    table_title = table.find("div", class_="section__title")
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
