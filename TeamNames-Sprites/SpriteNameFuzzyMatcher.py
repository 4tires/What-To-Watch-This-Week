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

In sprites - Sheet2: Duplicates sprites found that are two different teams.
Arsenal de Sarandi is Argentinian team with different logo..
[{'Arsenal': '[](#sprite2-p177)'}, {'Arsenal Sarandí': '[](#sprite2-p177)'}]

soccer wiki sprites https://www.reddit.com/r/soccerbot/wiki/index
"""
# Key used in TeamNames-Sprites.json... less to type
FSTN = 'FS_TeamName'

def spritesSheetCombinedReader():
    readSpriteTeamList = []
    returnSpriteTeamDict = {}
    returnTeamList = []
    with open('./TeamNames-Sprites/sprites - combined.csv', 'r', encoding='utf8') as readfile:
        reader = csv.reader(readfile, delimiter=';')
        for row in reader:
            readSpriteTeamList.append(row)
    for row in readSpriteTeamList:
        returnSpriteTeamDict[row[0]] = []
        for teamName in row[1:]:
            returnSpriteTeamDict[row[0]].append(teamName)
            returnTeamList.append(teamName)
    return returnSpriteTeamDict, returnTeamList

def jsonfunct():
    with open('./TeamNames-Sprites/TeamNames-Sprites.json', 'r', encoding='utf8') as j:
        jsonf = json.load(j)
    return jsonf

def acha_close_matches(team, teamlist, resultsSize, cutoff):
    return difflib.get_close_matches(team, teamlist, n=resultsSize, cutoff=cutoff)

def resultsprompts(resultsListIn):
    nolist = ['no', 'n', 'none']
    numberlist = []
    for item in resultsListIn:
        numberlist.append(str(item['n']))
        print(item['n'], ':', item['Team Name'], item['Sprite'])
    while True:
        response = input('Select correct team. Type "no" if no matches. ')
        if (str(response).lower() in nolist or str(response) in numberlist):
            break
        else:
            print('Invalid input. enter correct team name match or "no".\n')
    if str(response).lower() in nolist:
        return None
    else:
        tempList = (item for item in resultsListIn if item['n'] == int(response))
        return list(tempList)[0]

def fuzzyfunction(team, region, tList, sNDict):
    for cutoff, resultsSize in [[.9, 3], [.8, 6], [.6, 10], [.7, 5]]:
        if cutoff == .7:
            print(region, ':', team)
            userinputteam = input("Enter your best approximation of the team name: ")
            res = acha_close_matches(userinputteam, tList, resultsSize, cutoff)
        else:
            res = acha_close_matches(team, tList, resultsSize, cutoff)
        if res == []:
            continue
        print(region, ':', team)
        n = 0
        resultsDict = []
        for item in res:
            tempDict = {}
            tempDict['Team Name'] = item
            tempDict['Sprite'] = None
            for key, value in sNDict.items():
                if item in value:
                    sameSprite = 0
                    if len(resultsDict) == 0:
                        tempDict['Sprite'] = key
                        break
                    else:
                        dictSize = len(resultsDict)
                        for i in range(dictSize):
                            #if item in resultsDict[i]['Team Name']:
                            if key in resultsDict[i]['Sprite']:
                                sameSprite = 1
                                break
                    if sameSprite == 1:
                        continue
                    tempDict['Sprite'] = key
                    break
            if tempDict['Sprite'] != None:
                tempDict['n'] = n
                n += 1
                resultsDict.append(tempDict)
            else:
                continue
        match = resultsprompts(resultsDict)
        if match == None:
            continue
        return match['Team Name'], match['Sprite']
    print("No matches found. Moving on to next team...")
    return None, None

def main():
    spriteTeamDict, teamList  = spritesSheetCombinedReader()
    jsondict = jsonfunct()

    for region in jsondict:
        for item in jsondict[region]:
            if 'Sprite?' not in item:
                team = item[FSTN]
                match, sprite = fuzzyfunction(team, region, teamList, spriteTeamDict)
                if match != None:
                    item['Sprite?'] = 'Y'
                    item['Sprite'] = sprite
                    item['Proper Names'] = spriteTeamDict[sprite]
                else:
                    item['Sprite?'] = 'N'
                with open('./TeamNames-Sprites/TeamNames-Sprites.json', 'w', encoding='utf8') as j:
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