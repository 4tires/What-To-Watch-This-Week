from selenium import webdriver
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
from login_credentials import (
    username_credential,
    password_credential,
    chromedriver_path,
)
from json import load
import pyperclip
from dataclasses import dataclass
from typing import Optional
import re
from itertools import chain
from datetime import datetime, timedelta

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
    print("Login")
time.sleep(3)
username = driver.find_element(By.ID, "email")
username.clear()
username.send_keys(username_credential)

password = driver.find_element(By.NAME, "password")
password.clear()
password.send_keys(password_credential)
driver.find_element(By.CLASS_NAME, "wcl-button_eGaDi").click()

### CLASS DEFINING AND DICTIONARIES
wtwtw_matches_scrape = []
wtwtw_matches = []


@dataclass
class Match:
    time: str
    day: str
    match_id: str
    home: str
    away: str
    region: str
    competition: str
    round_name: Optional[str] = None
    home_sprite: Optional[str] = None
    away_sprite: Optional[str] = None
    competition_sprite: Optional[str] = None
    home_score: Optional[str] = None
    away_score: Optional[str] = None
    bold: bool = False


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

# Translate round names
round_translator = {
    "1/64-finals": "Round of 128",
    "1/32-finals": "Round of 64",
    "1/16-finals": "Round of 32",
    "1/8-finals": "Round of 16",
}

### SELENIUM FETCHING


def WTWTW():
    print("Fetching data from website")
    fetcher()
    driver.quit()
    print("All scraping done")
    all_fixtures = list(chain.from_iterable(wtwtw_matches_scrape))
    parsed_matches = parser(all_fixtures)
    matches_with_comp_sprites = insert_competition_sprites(parsed_matches)
    matches_with_all_sprites = insert_teams_sprites(matches_with_comp_sprites)
    bolded_matches = bold_prompt(matches_with_all_sprites)
    print("Writing Reddit post.")
    post_text = post_writer(bolded_matches)
    print(repr(post_text[:500]))  # inspect raw sprite chars survive this far
    pyperclip.copy(post_text)
    print("Completed.")
    print("Finished running WTWTW")
    return


def fetcher():
    days = 7
    for n in range(days):
        checked_matches = get_favourite_matches()
        wtwtw_matches_scrape.append(checked_matches)
        print("Completed day")
        if n == (days - 1):
            print("Completed all days")
            return
        driver.find_element(
            By.CSS_SELECTOR, "button[data-day-picker-arrow='next']"
        ).click()
        time.sleep(5)


def get_competition_and_region_for_match(match_div, soup):
    wrapper = match_div.find_previous(
        "div", class_="headerLeague__titleWrapper"
    )
    if wrapper is None:
        raise RuntimeError(
            f"No competition header found for match {match_div.get('id')}"
        )
    header = wrapper.find("a", class_="headerLeague__title")
    region = wrapper.find("span", class_="headerLeague__category-text")
    if header is None or region is None:
        raise RuntimeError(
            f"Incomplete competition header for match {match_div.get('id')}"
        )
    return header.get_text(strip=True), region.get_text(strip=True)


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
        competition_name, region_name = get_competition_and_region_for_match(
            match_div, soup
        )
        if needs_round_fetch(competition_name):
            competition_name = fetch_competition_with_round(
                match_div, main_window
            )
        match_div["data-competition-name"] = competition_name
        match_div["data-region-name"] = region_name

    # Assign date to each match
    for match_div in list_of_matches:
        match_div["data-date-day"] = date

    return list_of_matches


# TRANSFORMATION LOGIC
def parser(checked_matches):
    """
    Transforms raw starred-match Tags (from get_favourite_matches) into
    Match objects.
    """

    parsed_matches = []

    for fixture in checked_matches:

        # Time of match
        try:
            time = (
                fixture.find("div", class_="event__time")
                .get_text()
                .replace(":", "")
                .replace("FRO", "")
            )
        except:
            time = "No time"

        # Home and away teams
        home_team = fixture.find(
            "div", class_="event__homeParticipant"
        ).get_text()

        away_team = fixture.find(
            "div", class_="event__awayParticipant"
        ).get_text()

        # Remove countries in brackets in international competitions
        if " (" in home_team:
            home_team = home_team[: home_team.find(" (")]
        if " (" in away_team:
            away_team = away_team[: away_team.find(" (")]

        # Check if there was a first leg
        home_score = None
        away_score = None

        info_icon = fixture.find(
            "svg", attrs={"data-testid": "wcl-icon-settings-info-rounded"}
        )

        if info_icon is not None:
            aria_label = info_icon.get("aria-label", "")
            first_leg = re.search(
                r"First leg result:\s*(\d+)-(\d+)", aria_label
            )
            if first_leg is not None:
                # Label is ordered as leg 1 was played, i.e. home/away swapped
                # relative to this (leg 2) fixture.
                home_score, away_score = first_leg.group(1), first_leg.group(2)

        # Separate competition from round
        competition = None
        round_name = None
        comp_string = fixture["data-competition-name"]
        if "-" in comp_string:
            competition, round_name = comp_string.split("-", 1)
            competition = competition.strip()
            round_name = round_name.strip()
        else:
            competition = comp_string.strip()

        if round_name is not None and "Play Offs - " in round_name:
            round_name = round_name.split("-", 1)[-1].strip()

        # Translate rounds
        if round_name is not None and "1/" in round_name:
            round_name = round_translator.get(
                round_name, round_name
            )  # The 2nd round_name is a fallback in case the round is not in the dict

        # Append match

        parsed_matches.append(
            Match(
                time=time,
                day=fixture["data-date-day"],
                match_id=fixture["id"],
                home=home_team,
                away=away_team,
                region=fixture["data-region-name"].title(),
                competition=competition,
                round_name=round_name,
                home_score=home_score,
                away_score=away_score,
            )
        )
    return parsed_matches


# SPRITES LOGIC
def insert_competition_sprites(parsed_matches):
    with open(
        "./TeamNames-Sprites/CompNames-Sprites.json", "r", encoding="utf8"
    ) as rf:
        competition_sprite_json = load(rf)
    for fixture in parsed_matches:
        region_data = competition_sprite_json.get(fixture.region)
        if region_data is None:
            print(
                f"No region entry for '{fixture.region}' (fixture {fixture.match_id})"
            )
            continue

        comp_entry = region_data.get(fixture.competition)
        if comp_entry is None:
            print(
                f"No competition entry for '{fixture.competition}' in region '{fixture.region}' (fixture {fixture.match_id})"
            )
            continue

        sprite = comp_entry.get("Sprite")
        if sprite is None:
            print(
                f"No sprite found for '{fixture.competition}' (fixture {fixture.match_id})"
            )
            continue

        competition_name = comp_entry.get("Proper", fixture.competition)
        fixture.competition = competition_name
        fixture.competition_sprite = sprite

    return parsed_matches


def insert_teams_sprites(parsed_matches):
    with open(
        "./TeamNames-Sprites/TeamNames-Sprites.json", "r", encoding="utf8"
    ) as rf:
        team_sprite_json = load(rf)

    for fixture in parsed_matches:
        for side in ("home", "away"):
            team_name = getattr(fixture, side)
            entry = team_sprite_json.get(team_name)

            if entry is None:
                print(
                    f"No team entry for '{team_name}' (fixture {fixture.match_id})"
                )
                continue

            proper_name = entry.get("Proper")
            if proper_name is not None:
                setattr(fixture, side, proper_name)

            sprite = entry.get("Sprite")
            if sprite is None:
                print(
                    f"No sprite found for '{team_name}' (fixture {fixture.match_id})"
                )
                continue

            setattr(fixture, f"{side}_sprite", sprite)
    return parsed_matches


# REDDIT POST LOGIC
def group_fixtures_by_day(parsed_matches):
    fixtures_by_day = {}
    for fixture in parsed_matches:
        day_of_week = fixture.day.split(",")[0]
        fixtures_by_day.setdefault(day_of_week, []).append(fixture)
    return fixtures_by_day


def bold_prompt(parsed_matches):

    fixtures_by_day = group_fixtures_by_day(parsed_matches)

    no_list = ["n", "no", "none"]

    for day, fixtures in fixtures_by_day.items():
        print(f"\n--- {day} ---")
        for n, fixture in enumerate(fixtures):
            if (
                fixture.home_score is not None
                or fixture.away_score is not None
            ):
                score_str = f" ({fixture.home_score}-{fixture.away_score})"
            else:
                score_str = ""
            print(
                f"{n} : {fixture.home} vs {fixture.away}{score_str} in {fixture.competition}"
            )

        while True:
            print(
                "Select which fixtures to bold. Separate numbers with a space. "
                'For example: "1 2 3 4". Or enter [n, no, none] to bold none of the fixtures'
            )
            response = input("Make selection: ")
            if response.lower() in no_list:
                break
            selected = response.split()
            if all(
                item.isdigit() and int(item) < len(fixtures)
                for item in selected
            ):
                break
            print("\nInvalid input in fixture selection.")

        if response.lower() not in no_list:
            for n in response.split():
                fixtures[int(n)].bold = True

    return parsed_matches


def post_writer(parsed_matches):
    intro = (
        "These posts are as much for me as they are for you. So please feel free to reply "
        "with your suggestions for what to watch, and make a case for any game to be "
        "considered 'must watch', in which case I will bold it. The time zone used to sort "
        "games was LIS (Lisbon) time zone, so no, the game is not on a wrong date.\n\n---\n\n"
    )
    table_header = " Time (LIS / LIS -5) | Match | Competition | Round \n --------------|-----|-----------|-----|--- \n"

    fixtures_by_day = group_fixtures_by_day(parsed_matches)

    lines = [intro]

    for day, fixtures in fixtures_by_day.items():
        lines.append(f"\n***{day}***\n\n")
        lines.append(table_header)

        for fixture in sorted(fixtures, key=lambda f: f.time):
            if len(fixture.time) == 4:
                timestamp = datetime.strptime(fixture.time, "%H%M")
                timestamp_minus_5 = timestamp - timedelta(hours=5)
                timestamp_str = (
                    timestamp.strftime("%H:%M")
                    + " / "
                    + timestamp_minus_5.strftime("%H:%M")
                )
            else:
                timestamp_str = fixture.time

            fixture_cell = " vs "
            if (
                fixture.home_score is not None
                or fixture.away_score is not None
            ):
                fixture_cell = f" ({fixture.home_score}){fixture_cell}({fixture.away_score}) "

            home_part = (
                f"{fixture.home_sprite} {fixture.home}"
                if fixture.home_sprite
                else fixture.home
            )
            away_part = (
                f"{fixture.away} {fixture.away_sprite}"
                if fixture.away_sprite
                else fixture.away
            )
            fixture_cell = home_part + fixture_cell + away_part

            comp_cell = (
                f"{fixture.competition_sprite} {fixture.competition}"
                if fixture.competition_sprite
                else fixture.competition
            )

            round_cell = fixture.round_name if fixture.round_name else ""

            cells = [timestamp_str, fixture_cell, comp_cell, round_cell]

            if fixture.bold:
                row = " | ".join(f"**{c}**" if c else "" for c in cells)
            else:
                row = " | ".join(cells)

            lines.append(row + "\n")

    lines.append("\nr/WhatToWatchThisWeek")

    return "".join(lines)


input("Press Enter to Continue...")
WTWTW()
