import json
import csv
import difflib
import time

"""
Assumes you run this file from the "What-To-Watch-This-Week" folder



soccer wiki sprites https://www.reddit.com/r/soccerbot/wiki/index
"""

TNSDICT_LOCATE = './TeamNames-Sprites/TeamNames-Sprites-V2.json'
NAME_CORRECTOR_DICT = {
    'USA' : 'United States',
    'Bosnia and Herzegovina' : 'Bosnia-Herzegovina',
    'Macao' : 'Macau'
}

def main():
    with open('./TeamNames-Sprites/soccerbot-TeamNameSprites.json', 'r', encoding='utf8') as rj:
        sBTNSDict = json.load(rj)
    with open(TNSDICT_LOCATE, 'r', encoding='utf8') as rj:
        tNSDict = json.load(rj)
    for region in tNSDict:
        if region in NAME_CORRECTOR_DICT.keys():
            sBRegion = NAME_CORRECTOR_DICT[region]
        else:
            sBRegion = region
        if sBRegion not in sBTNSDict.keys():
            for item in tNSDict[region]:
                TNSDictWriter(tNSDict, region, item, None, None)
            continue
        elif len(sBTNSDict[sBRegion]) == 0:
            for item in tNSDict[region]:
                TNSDictWriter(tNSDict, region, item, None, None)
            continue
        else:
            teamNameList = list(sBTNSDict[sBRegion].keys())
        for item in tNSDict[region]:
            if 'Sprite' not in tNSDict[region][item].keys():
                fSTeamName = item
                tNMatch = FuzzyMatcher(fSTeamName, teamNameList, region)
                if tNMatch != None:
                    sprite = sBTNSDict[sBRegion][tNMatch]
                else:
                    sprite = None
                TNSDictWriter(tNSDict, region, item, tNMatch, sprite)
    return

def FuzzyMatcher(teamName, tNList, region):
    for cutoff, resultsSize in [[.9, 3], [.7, 5], [.6, 5]]:
        if (cutoff == .6):
            print(region, ':', teamName, ':', cutoff)
            print("Enter best approximation of team name or one of [s, skip] to skip.")
            userinput = input("Team name: ")
            if userinput in ['s', 'skip']:
                continue
            fuzzyMatches = difflib.get_close_matches(userinput, tNList, cutoff=cutoff, n=resultsSize)
        else:
            fuzzyMatches = difflib.get_close_matches(teamName, tNList, cutoff=cutoff, n=resultsSize)
        if fuzzyMatches == []:
            continue
        elif (cutoff == .9 and len(fuzzyMatches) == 1):
            print(region, ':', teamName, '- Match:', fuzzyMatches[0])
            return fuzzyMatches[0]
        print(region, ':', teamName, ':', cutoff)
        match = ResultsPrompt(fuzzyMatches, teamName)
        if match == None:
            continue
        return match
    print('No matches found. Moving on to next team..')
    return None

def ResultsPrompt(fMatchList, team):
    noList = ['no', 'n', 'none']
    numberList = []
    matchListLen = len(fMatchList)
    for n in range(matchListLen):
        numberList.append(str(n))
        matchingTeam = fMatchList[n]
        score = round(difflib.SequenceMatcher(None, fMatchList[n], team).ratio(), 4)
        print(n, ':', matchingTeam, ':', score)
    while True:
        response = input('Select correct team. Type [n, no, none] if no matches. ')
        if (str(response).lower() in noList or response in numberList):
            break
        else:
            print('Invalid input. Enter correct match or [n, no, none].')
    if response.lower() in noList:
        return None
    else:
        match = fMatchList[int(response)]
        return match

def TNSDictWriter(dictIn, region, club, properName, sprite):
    dictIn[region][club]['Proper'] = properName
    dictIn[region][club]['Sprite'] = sprite

    with open(TNSDICT_LOCATE, 'w', encoding='utf8') as wf:
        json.dump(dictIn, wf, indent=4, sort_keys=True)
    return

main()