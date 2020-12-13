# What-To-Watch-This-Week

 https://www.reddit.com/r/WhatToWatchThisWeek/

## Changelog

### v2

- Added Round
- Added Leg
- Added Aggregate

### v3

- Created two spreadsheets, one for input - to fill in the data - and another for output - to make the necessary process.

### v4

- Removed the aggregate column to become: Team A (2) vs (3) Team B

### v5

- Added Sprites

#### v5.1

- Added Sprites with official (standart) names to promote coherency and avoid spelling mistakes

### v6

- Added italic instead of just bold
- Added a circle (button) to clear only a few cells instead of all cells

### v7

- Removed italic
- Tried to change to excel (dropdown list search was bad even with add-in)
- Created a new spreadsheet to have all days of the week and tidy the sheets / formula to improve workflow								

### v8

- Use App Scripts to integrate all days and give a single text to copy

### v9

- Use Selenium to automate the fetching of the data (Still needs manual correcting because of differing linguistic terms e.g. Bayern Munich != Bayern Munch)
- Use vlookup to help with CL and EL groups

### v10

- Used BeautifulSoup to create a json file of links to each competition. Organized by region - country for domestic competitions, continent/region for continental competitions and international competitions. The json file is used to retrieve round and aggregate score for each match in WTWTW.py.

- imported requests and json/load
- created new function WTWTW to run entire script
- parser now returns data instead of writes to csv. Parser also retrieves date, region, and competition for later use. returns date and checked matches for that day
- Created WTWTWdict and competitionschecked dictionaries. WTWTWdict is used to store checked match data. competitionschecked tracks each region/competition from checked matches for later use.
- WTWTW function then iterates through competitionschecked for each league, and retreives the round and aggregate for each match in that competition in WTWTWmatches using competition_matches and acha_round functions. competition_matches returns a list of all the fixtures for the competition. acha_round parses through list for the match and returns round and aggregate. WTWTW adds round and aggregate to WTWTWmatches. WTWTW function then writes data to csv

## Backlog

- [ ] Create python dictionary to remove manual correction of team and league names (Linguistic differences as stated in v9) maybe use pickle for performance reasons
- [ ] Add automatic leg score
- [ ] Install Grid (needs Docker) to use python in spreadsheets easily
- [ ] (Hard) Automate round and group letter of the competition (e.g. "Semi-Final"; "Group B") as stated in v9
- [ ] Maybe ditch the spreadsheets (probably hard because of bold matches)
- [ ] Add more flairs (maybe use https://www.reddit.com/r/soccer/comments/f8z3sc/what_to_watch_this_week_241_march/fioh87b/)

## Technology Stack

- Github
- Python
- Requests
- Selenium

## Contribute

Feel free to contribute