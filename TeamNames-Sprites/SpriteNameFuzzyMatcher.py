import json
import csv
import difflib
import time

"""
Assumes you run this file from the "What-To-Watch-This-Week" folder



soccer wiki sprites https://www.reddit.com/r/soccerbot/wiki/index
"""
# Key used in TeamNames-Sprites.json... less to type
FSTN = 'FS_TeamName'

def main():
    with open('./TeamNames-Sprites/soccerbot-TeamNameSprites.json', 'r', encoding='utf8') as rj:
        sBTNSDict = json.load(rj)
    with open('./TeamNames-Sprites/TeamNames-Sprites.json', 'r', encoding='utf8') as rj:
        tNSDict = json.load(rj)
    for region in tNSDict:
        if region not in sBTNSDict.keys():
            continue
        else:
            teamNameList = list(sBTNSDict[region].keys())
        for item in tNSDict[region]:
            if 'Sprite' not in item.keys():
                fSTeamName = item['FS_TeamName']
                tNMatch = FuzzyMatcher(fSTeamName, teamNameList, region)
                if tNMatch != None:
                    item['Sprite'] = sBTNSDict[region][tNMatch]
                    item['Proper'] = tNMatch
                else:
                    item['Sprite'] = None
                with open('./TeamNames-Sprites/TeamNames-Sprites.json', 'w', encoding='utf8') as wf:
                    json.dump(tNSDict, wf, indent=4, sort_keys=True)
    return

def FuzzyMatcher(teamName, tNList, region):
    for cutoff, resultsSize in [[.9, 3], [.7, 5], [.6, 5]]:
        if (cutoff == .6):
            print(region, ':', teamName)
            print("Enter best approximation of team name or one of [s, skip] to skip.")
            userinput = input("Team name: ")
            if userinput in ['s', 'skip']:
                continue
            fuzzyMatches = difflib.get_close_matches(userinput, tNList, cutoff=cutoff, n=resultsSize)
        else:
            fuzzyMatches = difflib.get_close_matches(teamName, tNList, cutoff=cutoff, n=resultsSize)
        if fuzzyMatches == []:
            continue
        print(region, ':', teamName)
        match = ResultsPrompt(fuzzyMatches)
        if match == None:
            continue
        return match
    print('No matches found. Moving on to next team..')
    return None

def ResultsPrompt(fMatchList):
    noList = ['no', 'n', 'none']
    numberList = []
    matchListLen = len(fMatchList)
    for n in range(matchListLen):
        numberList.append(n)
        print(n, ':', fMatchList[n])
    while True:
        response = input('Select correct team. Type [n, no, none] if no matches. ')
        if (str(response).lower() in noList or int(response) in numberList):
            break
        else:
            print('Invalid input. Enter correct match or [n, no, none].')
    if response.lower() in noList:
        return None
    else:
        match = fMatchList[int(response)]
        return match

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