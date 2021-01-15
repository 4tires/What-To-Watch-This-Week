import difflib
import time
import csv

sprite1dict = {
    'Manchester United': '[](#sprite1-p2)',
    'Liverpool': '[](#sprite5-p334)',
    'Chelsea': '[](#sprite1-p4)',
    'Tottenham Hotspur': '[](#sprite1-p5)',
    'Barcelona': '[](#sprite1-p6)',
    'Bayern München': '[](#sprite1-p8)',
    'Real Madrid': '[](#sprite1-p9)',
    'Manchester City': '[](#sprite1-p10)',
    'Arsenal': '[](#sprite2-p177)',
    'Newcastle United': '[](#sprite1-p11)',
    'Borussia Dortmund': '[](#sprite1-p12)',
    'AC Milan': '[](#sprite1-p13)',
    'Seattle Sounders': '[](#sprite1-p14)',
    'Everton': '[](#sprite2-p49)',
    'Juventus': '[](#sprite5-p137)',
    'Celtic': '[](#sprite1-p18)',
    'Aston Villa': '[](#sprite1-p19)',
    'Portland Timbers': '[](#sprite1-p20)',
    'West Ham United': '[](#sprite1-p21)',
    'Sporting CP': '[](#sprite1-p222)'
    }
sprite2dict = {
    'Maidstone United': '[](#sprite1-p492)',
    'Manchester City': '[](#sprite1-p10)',
    'Manchester United': '[](#sprite1-p2)',
    'Mansfield Town': '[](#sprite2-p248)',
    'Marine': '[](#sprite2-p360)',
    'Matlock Town': '[](#sprite4-p497)',
    'Middlesbrough': '[](#sprite1-p91)',
    'Millwall': '[](#sprite1-p185)',
    'MK Dons': '[](#sprite1-p332)',
    'Morecambe': '[](#sprite1-p355)',
    'Newcastle United': '[](#sprite1-p11)',
    'Sporting Club de Portugal': '[](#sprite1-p222)'
    }
sprite1KeyList = list(sprite1dict.keys())
sprite2KeyList = list(sprite2dict.keys())

def acha_close_matches(team, teamlist, resultsSize, cutoff):
    return difflib.get_close_matches(team, teamlist, n=resultsSize, cutoff=cutoff)

def resultsprompts(resultsList):
    nolist = ['no', 'n', 'none']
    numberlist = []
    for item in resultsList:
        numberlist.append(str(item['n']))
        print(item['n'], ':', item['Team Name'])
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
        return (item for item in resultsList if item['n'] == str(response))

def newff(team, region, tList1, tList2, nSDict1, nSDict2):
    for cutoff, resultsSize in [[.9, 3], [.8, 6], [.6, 10], [.7, 5]]:
        if cutoff == .7:
            userinputteam = input("Enter your best approximation of the team name: ")
            results1 = acha_close_matches(userinputteam, tList1, resultsSize, cutoff)
            results2 = acha_close_matches(userinputteam, tList2, resultsSize, cutoff)
        else:
            results1 = acha_close_matches(team, tList1, resultsSize, cutoff)
            results2 = acha_close_matches(team, tList2, resultsSize, cutoff)
        if results1 == [] and results2 == []:
            continue
        print(region, ':', team)
        n = 0
        combinedResultsList = []
        if results1 != []:
            for item in results1:
                tempDict = {}
                tempDict['Team Name'] = item
                tempDict['Sprite'] = nSDict1[item]
                tempDict['Sheet'] = '1'
                tempDict['n'] = n
                n += 1
                combinedResultsList.append(tempDict)
        if results2 != []:
            sameTeamCheckDict = {}
            for item in results2:
                if nSDict2[item] in nSDict1.values():
                    sameTeamCheckDict[item] = nSDict2[item]

            for item in results2:
                if nSDict2[item] in sameTeamCheckDict.values():
                    print('Same team found in sheet 2.', item)
                    continue
                tempDict = {}
                tempDict['Team Name'] = item
                tempDict['Sprite'] = nSDict2[item]
                tempDict['Sheet'] = '2'
                tempDict['n'] = n
                n += 1
                combinedResultsList.append(tempDict)
        match = resultsprompts(combinedResultsList)
        print(match)
        if match == None:
            continue
        sameteam = None
        sprite = match['Sprite']
        if match['Sheet'] == '1':
            for key, value in nSDict2.items():
                if sprite == value:
                    sameteam = key
                    break
        else:
            for key, value in nSDict1.items():
                if sprite == value:
                    sameteam = key
                    break
        return match, sameteam, sprite
    print("No matches found. Moving on to next team...")
    return None, None, None


 
            

#newff('Manchester Utd', 'Portugal', sprite1KeyList, sprite2KeyList, sprite1dict, sprite2dict)

"""
    for list, dict, otherdict in [[tList1, nSDict1, nSDict2], [tList2, nSDict2, nSDict1]]:
        for cutoff, resultsSize in [[.9, 3], [.8, 6], [.6, 10], [.7, 5]]:
            if cutoff != .7:
                results = acha_close_matches(team, list, resultsSize, cutoff)
                if results == []:
                    continue
                print(region, ":", team)
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
                print(region, team)
                userinputteam = input("Enter your best approximation of the team name: ")
                results = acha_close_matches(userinputteam, list, resultsSize, cutoff)
                if results == []:
                    print("No results.")
                    continue
                print(region)
                print("FS Team Name:", team)
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
    return None, None, None"""

"""
def originalff(team, region, tList1, tList2, nSDict1, nSDict2):

    for list, dict, otherdict in [[tList1, nSDict1, nSDict2], [tList2, nSDict2, nSDict1]]:
        for cutoff, resultsSize in [[.9, 3], [.8, 6], [.6, 10], [.7, 5]]:
            if cutoff != .7:
                results = acha_close_matches(team, list, resultsSize, cutoff)
                if results == []:
                    continue
                print(region, ":", team)
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
                print(region, team)
                userinputteam = input("Enter your best approximation of the team name: ")
                results = acha_close_matches(userinputteam, list, resultsSize, cutoff)
                if results == []:
                    print("No results.")
                    continue
                print(region)
                print("FS Team Name:", team)
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
    return None, None, None"""


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

spritesDict1 = spritesSheet1()
spritesDict2 = spritesSheet2()



sprites2KeyList = list(spritesDict2.keys())
sprites2ValList = list(spritesDict2.values())

"""
with open('TeamNames-Sprites\sprites - combined.csv', 'w', encoding='utf8', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=';')

        
        writer.writerow([key, value])"""
n = 0
m = 0
j = 0
spritesCombinedDict = {}
for dict in [spritesDict1, spritesDict2]:
    for key, value in dict.items():
        if key not in spritesCombinedDict.keys():
            spritesCombinedDict[key] = value
        else:
            for item in value:
                if item not in spritesCombinedDict[key]:
                    spritesCombinedDict[key].append(item)
print(spritesCombinedDict['[](#sprite8-p427)'])
with open('TeamNames-Sprites\sprites - combined.csv', 'w', encoding='utf8', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=';')
    for key, value in spritesCombinedDict.items():
        writer.writerow([key, value])

"""for key, value in spritesDict2.items():
    if value in spritesDict1.values() and key in spritesDict1.keys():
        print("exact match.", key, 'and', value)
        n += 1
        continue
    elif value in spritesDict1.values() and key not in spritesDict1.keys():
        m += 1
        print('sprite match, but not team.', key, 'and', value)
    elif key in spritesDict1.keys() and value not in spritesDict1.values():
        print("matching team name with different sprite.", key, value )
        j += 1

    writer.writerow([key, value])
print('total exact matches =', n)
print('total sprite matches =', m)
print('total team name matches =', j)"""