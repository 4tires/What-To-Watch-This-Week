import difflib
import time
import csv
from typing import OrderedDict
import pprint
import json
import re

with open('./TeamNames-Sprites/TeamNames-Sprites-V2.json', 'r', encoding='utf8') as rf:
    tNSDict = json.load(rf)

def DuplicateTeamNameChecker(teamIn, regionIn):
    for region, teamDict in tNSDict.items():
        if regionIn == region:
            continue
        else:
            teamList = list(teamDict.keys())
            for team in teamList:
                if teamIn == team:
                    printText = (regionIn, teamIn, ":", region, team)
                    print('Duplicate found!', printText)
    return

for region, teamList in tNSDict.items():
    for teamName in teamList.keys():
        DuplicateTeamNameChecker(teamName, region)

