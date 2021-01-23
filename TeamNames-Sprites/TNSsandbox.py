import difflib
import time
import csv
from typing import OrderedDict

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
    if response.lower() in nolist:
        return None
    else:
        return (item for item in resultsListIn if item['n'] == str(response))

def newff(team, region, tList, sNDict):
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
        print(match)
        if match == None:
            continue
        sprite = match['Sprite']
        return match['Team Name'], sprite
    print("No matches found. Moving on to next team...")
    return None, None

def spritesSheet1():
    readteamlist = []
    returnteamdict = {}
    with open('TeamNames-Sprites\\sprites - Sheet1.tsv', encoding='utf8') as readfile:
        reader = csv.reader(readfile, delimiter='\t')
        for row in reader:
            readteamlist.append(row)
    for row in readteamlist:
        sprite = row[1].replace(row[0], '')
        if sprite in returnteamdict.keys():
            if row[0] not in returnteamdict[sprite]:
                returnteamdict[sprite].append(row[0])
        else:
            returnteamdict[sprite] = [row[0]]
    return returnteamdict

def spritesSheet2():
    readteamlist = []
    returnteamdict = {}
    with open('TeamNames-Sprites\\sprites - Sheet2.csv', encoding='utf8') as readfile:
        reader = csv.reader(readfile, delimiter=';')
        for row in reader:
            readteamlist.append(row)
    for row in readteamlist:
        if row[2] in returnteamdict.keys():
            if row[1] not in returnteamdict[row[2]]:
                returnteamdict[row[2]].append(row[1])
        else:
            returnteamdict[row[2]] = [row[1]]
    return returnteamdict

def spritesSheetCombinedwriter():
    spritesDict1 = spritesSheet1()
    spritesDict2 = spritesSheet2()
    spriteTeamDict = {}
    for spritesDict in [spritesDict1, spritesDict2]:
        for key, value in spritesDict.items():
            if key not in spriteTeamDict.keys():
                spriteTeamDict[key] = []
                for val in value:
                    spriteTeamDict[key].append(val)
            else:
                for val in value:
                    if val not in spriteTeamDict[key]:
                        spriteTeamDict[key].append(val)

    with open('./TeamNames-Sprites/sprites - combined.csv', 'w', encoding='utf8', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        for key, value in spriteTeamDict.items():
            temp = [key]
            for val in value:
                temp.append(val)
            writer.writerow(temp)
    return

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

spriteTeamDict, teamList = spritesSheetCombinedReader() 
newff('Wuppertaler', "Place", teamList, spriteTeamDict)