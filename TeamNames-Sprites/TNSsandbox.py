import difflib
import time
import csv
from typing import OrderedDict
import pprint
import json
import re

estoniaFS = {
    "Elva": {},
    "Flora": {},
    "JK Jarve": {},
    "Kalju": {},
    "Kuressaare": {},
    "Legion": {},
    "Levadia": {},
    "Maardu": {},
    "Narva": {},
    "Nomme Utd": {},
    "Paide": {},
    "Parnu": {},
    "Parnu JK Vaprus": {},
    "Tammeka": {},
    "Tulevik": {},
    "Vandra Vaprus": {}
}
estoniaSB = {
    "Flora": "[](#sprite5-p392)",
    "Infonet": "[](#sprite5-p394)",
    "Levadia Tallinn": "[](#sprite5-p391)",
    "Narva Trans": "[](#sprite5-p397)",
    "N\u00f5mme Kalju": "[](#sprite2-p101)",
    "Paide Linnameeskond": "[](#sprite4-p281)",
    "P\u00e4rnu Linnameeskond": "[](#sprite5-p396)",
    "St. Rakvere JK Tarvas": "[](#sprite7-p90)",
    "Sillam\u00e4e Kalev": "[](#sprite5-p393)",
    "Tallinna Kalev": "[](#sprite8-p346)",
    "Tartu-Tammeka": "[](#sprite4-p209)",
    "Viljandi Tulevik": "[](#sprite5-p395)"
}
'''for sBTeam in estoniaSB:
    sBTeamSplit = re.split(r"[. \-]+", sBTeam)
    print(sBTeamSplit)'''
print('Nomme', "N\u00f5mme")
print(difflib.SequenceMatcher(None, 'Nomme', "N\u00f5mme").ratio())

def FirstPieceMealFuzzyMatcher(teamName, tNList):
    matchDict = {}
    matchDict[teamName] = {}
    fuzzymatches = []
    for sBTeam in tNList:
        sBTeamSplit = re.split(r"[. \-]+", sBTeam)
        tNSplit = re.split(r"[. \-]+", teamName)
        wordMatch = []
        for word in tNSplit:
            if len(word) > 2:
                wordMatch = difflib.get_close_matches(word, sBTeamSplit, cutoff=.8, n=3)
            for match in wordMatch:
                matchDict[teamName][sBTeam] = match, round(difflib.SequenceMatcher(None, word, match).ratio(), 3)
    print('{FS Team Name: {SB Team Name: (matching substring, score)}}')
    print(matchDict)
    
    return None

def PieceMealFuzzyMatcher(teamName, tNList):
    fuzzymatches = []
    tNSplit = re.split(r"[. \-]+", teamName)
    for sBTeam in tNList:
        sBTeamSplit = re.split(r"[. \-]+", sBTeam)
        wordMatch = []
        for word in tNSplit:
            if len(word) > 2:
                wordMatch = difflib.get_close_matches(word, sBTeamSplit, cutoff=.8, n=3)
            if len(wordMatch) != 0:
                fuzzymatches.append(sBTeam) 
    
    return fuzzymatches

teamNameList = list(estoniaSB.keys())
for item in estoniaFS:
    print(item)
    tNMatch = PieceMealFuzzyMatcher(item, teamNameList)
    print(tNMatch)
    input('Enter...')
