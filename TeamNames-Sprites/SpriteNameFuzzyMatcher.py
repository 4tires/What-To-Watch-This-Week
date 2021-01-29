import json
import csv
import difflib
import time
import re

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
                #tNMatch = OnlyPt9orBetterFuzzyMatcher(fSTeamName, teamNameList)
                tNMatch = FuzzyMatcher(fSTeamName, teamNameList, region)
                if tNMatch != None:
                    sprite = sBTNSDict[sBRegion][tNMatch]
                else:
                    sprite = None
                    #continue
                TNSDictWriter(tNSDict, region, item, tNMatch, sprite)
    return

def OnlyPt9orBetterFuzzyMatcher(teamName, tNList):
    fuzzyMatches = difflib.get_close_matches(teamName, tNList, cutoff=.901, n=2)
    if len(fuzzyMatches) == 1:
        return fuzzyMatches[0]
    return None

def SubstringFuzzyMatcher(teamName, tList, returnSize):
    returnSSFuzzyMatches = {}
    tNSplit = re.split(r"[. \-]+", teamName)
    for clubFromtList in tList:
        clubSplit = re.split(r"[. \-]+", clubFromtList)
        returnSSFuzzyMatches[clubFromtList] = 0
        for word in tNSplit:
            wordMatch = []
            if (len(word) < 3):
                continue
            else:
                wordMatch = difflib.get_close_matches(word, clubSplit, cutoff=.8, n=1)
            for w in wordMatch:
                score = difflib.SequenceMatcher(None, word, w).ratio()
                if score > returnSSFuzzyMatches[clubFromtList]:
                    returnSSFuzzyMatches[clubFromtList] = score
    for i in list(returnSSFuzzyMatches):
        if returnSSFuzzyMatches[i] == 0:
            del returnSSFuzzyMatches[i]
    returnSSFuzzyMatches = dict(sorted(returnSSFuzzyMatches.items(), key=lambda item: item[1], reverse=True))
    return list(returnSSFuzzyMatches.keys())[:returnSize]

def FuzzyMatcher(teamName, tNList, region):
    for cutoff, resultsSize in [[.85, 3], [.6, 5], [.8, 5], [.55, 5]]:
        if (cutoff == .8):
            fuzzyMatches = SubstringFuzzyMatcher(teamName, tNList, resultsSize)
        elif (cutoff == .55):
            print('\n', region, ':', teamName, ':', cutoff)
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
        print('\n', region, ':', teamName, ':', cutoff)
        match = ResultsPrompt(fuzzyMatches, teamName)
        if match == '--skip--':
            break
        elif match != None:
            return match
    print('No matches found. Moving on to next team..')
    return None

def ResultsPrompt(fMatchList, team):
    noList = ['no', 'n', 'none']
    skipList = ['s', 'skip']
    numberList = []
    matchListLen = len(fMatchList)
    for n in range(matchListLen):
        numberList.append(str(n))
        matchingTeam = fMatchList[n]
        score = round(difflib.SequenceMatcher(None, fMatchList[n], team).ratio(), 4)
        print(n, ':', matchingTeam, ':', score)
    while True:
        response = input('Select correct team. Type [n, no, none] if no matches. ')
        strch = str(response).lower()
        if (strch in noList or strch in skipList or response in numberList):
            break
        else:
            print('Invalid input. Enter correct match or [s, skip, n, no, none].')
    if response.lower() in noList:
        return None
    elif response.lower() in skipList:
        return '--skip--'
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