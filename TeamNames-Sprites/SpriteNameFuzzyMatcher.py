import json
import csv
import difflib
import time

"""
Assumes you run this file from the "What-To-Watch-This-Week" folder

List of teams/countries/letters (row 856?) that have sprites:
https://docs.google.com/spreadsheets/d/1EEhmViH89l1lqv3vrz0MxfefUCc-SGTmi0FW90by2b4/edit#gid=0
Additional links:
https://www.reddit.com/r/soccer/comments/bkdkux/is_your_clubs_flair_missing_from_rsoccer_does_it/
https://www.reddit.com/r/soccer/wiki/flairmr (has link to google spreadsheet above)

In sprites - Sheet2: Duplicates sprites found that are two differen teams.
Arsenal Sarandi is Argentinian team with different logo..
[{'Arsenal': '[](#sprite2-p177)'}, {'Arsenal Sarandí': '[](#sprite2-p177)'}]

"""
# Key used in TeamNames-Sprites.json
FSTN = 'FS_TeamName'

def spritesSheet1():
    readteamlist = []
    returnteamdict = {}

    with open('TeamNames-Sprites\\sprites - Sheet1.tsv', encoding='utf8') as readfile:
        reader = csv.reader(readfile, delimiter='\t')
        for row in reader:
            readteamlist.append(row)

    for row in readteamlist:
        returnteamdict[row[0]] = row[1].replace(row[0], '')
    return returnteamdict

def spritesSheet2():
    readteamlist = []
    returnteamdict = {}

    with open('TeamNames-Sprites\\sprites - Sheet2.csv', encoding='utf8') as readfile:
        reader = csv.reader(readfile, delimiter=';')
        for row in reader:
            readteamlist.append(row)

    for row in readteamlist:
        returnteamdict[row[1]] = row[2]
    return returnteamdict

def duplicatechecker(spriteSheetfunct):
    teamToSpriteDict = spriteSheetfunct()
    spriteList = list(teamToSpriteDict.values())
    returnDuplicatesDict = {}
    for valueSprite in spriteList:
        if valueSprite in returnDuplicatesDict.keys():
            pass
        tempDuplicatesList = []
        for key, value in teamToSpriteDict.items():
            tempDict = {}
            if valueSprite == value:
                tempDict[key] = value
                tempDuplicatesList.append(tempDict)
        if (len(tempDuplicatesList) > 1):
            returnDuplicatesDict[valueSprite] = tempDuplicatesList
    return returnDuplicatesDict

def jsonfunct():
    with open('TeamNames-Sprites\\TeamNames-Sprites.json', 'r', encoding='utf8') as j:
        jsonf = json.load(j)
    return jsonf

def acha_close_matches(team, teamlist, resultsSize, cutoff):
    return difflib.get_close_matches(team, teamlist, n=resultsSize, cutoff=cutoff)

def resultsprompts(list):
    nolist = ['no', 'n', 'none']
    listlen = len(list)
    numberlist = []
    for n in range(listlen):
        numberlist.append(str(n))
        print(n, " : ", list[n])
    while True:
        response = input('Select correct team. Type "no" if no matches. ')
        if (str(response).lower() in nolist or str(response) in numberlist):
            break
        else:
            print('Invalid input. enter correct team name match or "no".')
            time.sleep(.5)
    if response.lower() in nolist:
        return None
    else:
        return list[int(response)]

def fuzzyfunction(team, region, tList1, tList2, nSDict1, nSDict2):

    for list, dict, otherdict in [[tList1, nSDict1, nSDict2], [tList2, nSDict2, nSDict1]]:
        for cutoff, resultsSize in [[.9, 3], [.8, 6], [.6, 10], [.7, 5]]:
            if cutoff != .7:
                results = acha_close_matches(team, list, resultsSize, cutoff)
                if results == []:
                    continue
                print(region, ':', team)
                match = resultsprompts(results)
                sameteam = None
                if match == None:
                    continue
                sprite = dict[match]
                for key, value in otherdict.items():
                    if sprite == value:
                        sameteam = key
                        break
                return match, sameteam, sprite
            else:
                print(region, ':', team)
                userinputteam = input("Enter your best approximation of the team name: ")
                results = acha_close_matches(userinputteam, list, resultsSize, cutoff)
                if results == []:
                    print("No results.")
                    continue
                print(region, ':', team)
                match = resultsprompts(results)
                sameteam = None
                if match == None:
                    continue
                sprite = dict[match]
                for key, value in otherdict.items():
                    if sprite == value:
                        sameteam = key
                        break
                return match, sameteam, sprite
    
    print("No matches found. Moving on to next team...")
    return None, None, None

def main():
    teamNameSpritesDict1 = spritesSheet1()
    teamNameSpritesDict2 = spritesSheet2()
    teamList1 = list(teamNameSpritesDict1.keys())
    teamList2 = list(teamNameSpritesDict2.keys())

    jsondict = jsonfunct()
    for region in jsondict:
        for item in jsondict[region]:
            if 'Sprite?' not in item:
                team = item[FSTN]
                match, alsomatch, sprite = fuzzyfunction(team, region, teamList1, teamList2, teamNameSpritesDict1, teamNameSpritesDict2)
                if match != None:
                    item['Sprite?'] = 'Y'
                    item['Sprite'] = sprite
                    if alsomatch in [None, match]:
                        item['Proper Names'] = [match]
                    else:
                        item['Proper Names'] = [match, alsomatch]
                else:
                    item['Sprite?'] = 'N'
                with open('TeamNames-Sprites\\TeamNames-Sprites.json', 'w', encoding='utf8') as j:
                    json.dump(jsondict, j, sort_keys=True, indent=4)

    return
main()


"""
For each team in json file:
    Fuzzy match search in sprites - Sheet1
    if results found present and prompt user to select
        if none selected raise cutoff and fuzzy match search again. Repeat x times.
        if result selected search in sprites - Sheet2 for matching sprite and prompt user to confirm.
            if not confirmed same team add original selection to team dict in json
            if confirmed same team add both to team dict in json
        after x times prompt user to type team name or enter NA to skip this team and start with the next
            search user input, prompt user to select from results
    Repeat with fuzzy match search in sprites - SHeet 2
             


"""