from datetime import datetime, timedelta
import WTWTW
"""
WTWTWmatches = {
    '12/02 Fr': [
        {'Time': '1430', 'id': 'g_1_CUdei8nM', 'Home': 'RB Leipzig', 'Away': 'FC Augsburg', 'Region': 'Germany', 'Competition': 'Bundesliga', 'Round': None, 'H Sprite': '[](#sprite5-p14)', 'A Sprite': '[](#sprite1-p291)'}, 
        {'Time': '1530', 'id': 'g_1_4Qrd1u9r', 'Home': 'Famalicão', 'Away': 'Belenenses', 'Region': 'Portugal', 'Competition': 'Primeira Liga', 'Round': None, 'H Sprite': '[](#sprite8-p345)', 'A Sprite': '[](#sprite2-p201)'}],
    '13/02 Sa': [
        {'Time': '0730', 'id': 'g_1_YDUBJOHU', 'Home': 'Leicester City', 'Away': 'Liverpool', 'Region': 'England', 'Competition': 'Premier League', 'Round': None, 'H Sprite': '[](#sprite1-p87)', 'A Sprite': '[](#sprite1-p3)'}, 
        {'Time': '1100', 'id': 'g_1_W8jdixKS', 'Home': 'Paris Saint-Germain', 'Away': 'OGC Nice', 'Region': 'France', 'Competition': 'Ligue 1', 'Round': None, 'H Sprite': '[](#sprite1-p35)', 'A Sprite': '[](#sprite2-p71)'},
        {'Time': '0930', 'id': 'g_1_U57jhlXF', 'Home': 'Borussia Dortmund', 'Away': '1899 Hoffenheim', 'Region': 'Germany', 'Competition': 'Bundesliga', 'Round': None, 'H Sprite': '[](#sprite1-p12)', 'A Sprite': '[](#sprite1-p353)'}],
    '14/02 Su': [
        {'Time': '0700', 'id': 'g_1_lQ4LwS2n', 'Home': 'Southampton', 'Away': 'Wolves', 'Region': 'England', 'Competition': 'Premier League', 'Round': None, 'H Sprite': '[](#sprite1-p38)', 'A Sprite': '[](#sprite1-p70)'},
        {'Time': '0900', 'id': 'g_1_61aQxnIh', 'Home': 'West Bromwich Albion', 'Away': 'Manchester United', 'Region': 'England', 'Competition': 'Premier League', 'Round': None, 'H Sprite': '[](#sprite1-p78)', 'A Sprite': '[](#sprite1-p2)'},
        {'Time': '1500', 'id': 'g_1_SvxSoGsj', 'Home': 'Bordeaux', 'Away': 'Olympique de Marseille', 'Region': 'France', 'Competition': 'Ligue 1', 'Round': None, 'H Sprite': '[](#sprite1-p271)', 'A Sprite': '[](#sprite1-p119)'}],
    '15/02 Mo': [
        {'Time': '1430', 'id': 'g_1_jF8ngUH9', 'Home': 'Bayern München', 'Away': 'Arminia Bielefeld', 'Region': 'Germany', 'Competition': 'Bundesliga', 'Round': None, 'H Sprite': '[](#sprite1-p8)', 'A Sprite': '[](#sprite1-p290)'},
        {'Time': '1515', 'id': 'g_1_S4iU5L0R', 'Home': 'Sporting Clube de Portugal', 'Away': 'Paços de Ferreira', 'Region': 'Portugal', 'Competition': 'Primeira Liga', 'Round': None, 'H Sprite': '[](#sprite1-p52)', 'A Sprite': '[](#sprite4-p277)'},
        {'Time': '0825', 'id': 'g_1_Iy1mZ4v0', 'Home': 'Saham', 'Away': 'Al Seeb', 'Region': 'Oman', 'Competition': 'Sultan Cup', 'Round': 'Quarter-finals', 'H Sprite': None, 'A Sprite': None, 'H FL Score': '0', 'A FL Score': '1'},
        {'Time': '1115', 'id': 'g_1_8Qg0W2OI', 'Home': 'Al-Msnaa', 'Away': 'Dhofar', 'Region': 'Oman', 'Competition': 'Sultan Cup', 'Round': 'Quarter-finals', 'H Sprite': None, 'A Sprite': None, 'H FL Score': '0', 'A FL Score': '2'}],
    '16/02 Tu': [
        {'Time': '1500', 'id': 'g_1_0EuFOHl3', 'Home': 'Barcelona', 'Away': 'Paris Saint-Germain', 'Region': 'Europe', 'Competition': 'Champions League', 'Round': 'Round of 16', 'H Sprite': '[](#sprite1-p6)', 'A Sprite': '[](#sprite1-p35)', 'H FL Score': None, 'A FL Score': None},
        {'Time': '1500', 'id': 'g_1_KI2S0Edd', 'Home': 'RB Leipzig', 'Away': 'Liverpool', 'Region': 'Europe', 'Competition': 'Champions League', 'Round': 'Round of 16', 'H Sprite': '[](#sprite5-p14)', 'A Sprite': '[](#sprite1-p3)', 'H FL Score': None, 'A FL Score': None}],
    '17/02 We': [
        {'Time': '1515', 'id': 'g_1_OlvMm9VH', 'Home': 'Everton', 'Away': 'Manchester City', 'Region': 'England', 'Competition': 'Premier League', 'Round': None, 'H Sprite': '[](#sprite1-p15)', 'A Sprite': '[](#sprite1-p10)'},
        {'Time': '1500', 'id': 'g_1_KfKuAIZ9', 'Home': 'FC Porto', 'Away': 'Juventus', 'Region': 'Europe', 'Competition': 'Champions League', 'Round': 'Round of 16', 'H Sprite': '[](#sprite1-p37)', 'A Sprite': '[](#sprite1-p17)', 'H FL Score': None, 'A FL Score': None},
        {'Time': '1500', 'id': 'g_1_h8Im8d4M', 'Home': 'Sevilla', 'Away': 'Borussia Dortmund', 'Region': 'Europe', 'Competition': 'Champions League', 'Round': 'Round of 16', 'H Sprite': '[](#sprite1-p229)', 'A Sprite': '[](#sprite1-p12)', 'H FL Score': None, 'A FL Score': None}],
    '18/02 Th': [
        {'Time': '1255', 'id': 'g_1_YcQSreg1', 'Home': 'SC Braga', 'Away': 'AS Roma', 'Region': 'Europe', 'Competition': 'Europa League', 'Round': 'Round of 32', 'H Sprite': '[](#sprite1-p342)', 'A Sprite': '[](#sprite1-p36)', 'H FL Score': None, 'A FL Score': None},
        {'Time': '1255', 'id': 'g_1_xWWJpHOl', 'Home': 'Real Sociedad', 'Away': 'Manchester United', 'Region': 'Europe', 'Competition': 'Europa League', 'Round': 'Round of 32', 'H Sprite': '[](#sprite1-p237)', 'A Sprite': '[](#sprite1-p2)', 'H FL Score': None, 'A FL Score': None},
        {'Time': '1255', 'id': 'g_1_QeeljIqU', 'Home': 'Wolfsberger AC', 'Away': 'Tottenham Hotspur', 'Region': 'Europe', 'Competition': 'Europa League', 'Round': 'Round of 32', 'H Sprite': '[](#sprite5-p294)', 'A Sprite': '[](#sprite1-p5)', 'H FL Score': None, 'A FL Score': None},
        {'Time': '1500', 'id': 'g_1_vykXgL12', 'Home': 'Red Bull Salzburg', 'Away': 'Villarreal', 'Region': 'Europe', 'Competition': 'Europa League', 'Round': 'Round of 32', 'H Sprite': '[](#sprite1-p455)', 'A Sprite': '[](#sprite1-p270)', 'H FL Score': None, 'A FL Score': None}]
    }
"""

WTWTWmatches2 = {
    '28/02 Su': [
        {'Time': '0730','C Sprite' : None, 'id': 'g_1_YDUBJOHU', 'Home': 'Leicester City', 'Away': 'Liverpool', 'Region': 'England', 'Competition': 'Premier League', 'Round': None, 'H Sprite': '[](#sprite1-p87)', 'A Sprite': '[](#sprite1-p3)'}, 
        {'Time': '1100','C Sprite' : None, 'id': 'g_1_W8jdixKS', 'Home': 'Paris Saint-Germain', 'Away': 'OGC Nice', 'Region': 'France', 'Competition': 'Ligue 1', 'Round': None, 'H Sprite': '[](#sprite1-p35)', 'A Sprite': '[](#sprite2-p71)'},
        {'Time': '0930','C Sprite' : None, 'id': 'g_1_U57jhlXF', 'Home': 'Borussia Dortmund', 'Away': '1899 Hoffenheim', 'Region': 'Germany', 'Competition': 'Bundesliga', 'Round': None, 'H Sprite': '[](#sprite1-p12)', 'A Sprite': '[](#sprite1-p353)'}],
    '01/03 Mo': [
        {'Time': '1430','C Sprite' : None, 'id': 'g_1_CUdei8nM', 'Home': 'RB Leipzig', 'Away': 'FC Augsburg', 'Region': 'Germany', 'Competition': 'Bundesliga', 'Round': None, 'H Sprite': '[](#sprite5-p14)', 'A Sprite': '[](#sprite1-p291)'}, 
        {'Time': '1530','C Sprite' : None, 'id': 'g_1_4Qrd1u9r', 'Home': 'Famalicão', 'Away': 'Belenenses', 'Region': 'Portugal', 'Competition': 'Primeira Liga', 'Round': None, 'H Sprite': '[](#sprite8-p345)', 'A Sprite': '[](#sprite2-p201)'},
        {'Time': '1115', 'C Sprite' : None, 'id': 'g_1_8Qg0W2OI', 'Home': 'Al-Msnaa', 'Away': 'Dhofar', 'Region': 'Oman', 'Competition': 'Sultan Cup', 'Round': 'Quarter-finals', 'H Sprite': None, 'A Sprite': None, 'H FL Score': '0', 'A FL Score': '2'}]
}

dayOfWeek = {
    'Mo' : 'Monday',
    'Tu' : 'Tuesday',
    'We' : 'Wednesday',
    'Th' : 'Thursday',
    'Fr' : 'Friday',
    'Sa' : 'Saturday',
    'Su' : 'Sunday'
}
def WTWTW_main():
    input('Press Enter to Continue...')
    WTWTWmatches = WTWTW.WTWTW()
    for date in WTWTWmatches:
        noList = ['n', 'no', 'none']
        numberList = []
        for n in range(len(WTWTWmatches[date])):
            WTWTWmatches[date][n]['Bold'] = 0
            promptText = ''
            for item in [WTWTWmatches[date][n]['Home'], 'vs', WTWTWmatches[date][n]['Away'], 'in', WTWTWmatches[date][n]['Competition']]:
                promptText = promptText + item + ' '
            numberList.append(str(n))
            print(str(n) + ' : ' + promptText)
        while True:
            print('Select which matches to bold. Separate numbers with a space. For example: "1 2 3 4". Or enter [n, no, none] to bold none of the matches')
            response = input('Make selection: ')
            if (response.lower() in noList):
                break
            check = all(item in numberList for item in response.split(' '))
            if check:
                break
            else:
                print('\nInvalid input in match selection.')
        if response.lower() not in noList:
            matchesToBold = response.split(' ')
            for n in matchesToBold:
                WTWTWmatches[date][int(n)]['Bold'] = 1
    print('Writing reddit post.')
    WTWTW_Post(WTWTWmatches)
    print('Completed.')
        


def WTWTW_Post(writeReadyMatchDict):
    intro = "These posts are as much for me as they are for you. So please feel free to reply with your suggestions for what to watch, and make a case for any game to be considered 'must watch', in which case I will bold it. The time zone used to sort games was LIS (Lisbon) time zone, so no, the game is not on a wrong date.\n\n---\n\n"
    tableHeader = ' Time (LIS / LIS -5) | Match | Competition | Round \n --------------|-----|-----------|-----|--- \n'
    with open('./WTWTW_post.txt', 'w', encoding='utf8') as wf:
        wf.write(intro)
        for dateday in writeReadyMatchDict:
            day = dateday.split(' ')[1]
            wf.write('\n***' + dayOfWeek[day] + '***\n\n')
            wf.write(tableHeader)
            for match in sorted(writeReadyMatchDict[dateday], key=lambda i: i['Time']):
                if len(match['Time']) == 4:
                    timestamp = datetime.strptime(match['Time'], '%H%M')
                    tSMinus5 = timestamp - timedelta(hours=5)
                    timestamp = timestamp.strftime("%H:%M")
                    tSMinus5 = tSMinus5.strftime("%H:%M")
                    timestamp = timestamp + ' / ' + tSMinus5                 
                else:
                    timestamp = match['Time']
                matchCell = ' vs '
                try:
                    if match['H FL Score'] != None or match['A FL Score'] != None:
                        matchCell = ' (' + match['H FL Score'] + ')' + matchCell + '(' + match['A FL Score'] + ') '
                except (KeyError, TypeError) as e:
                    pass
                try:
                    matchCell = match['H Sprite'] + ' ' + match['Home'] + matchCell
                except (KeyError, TypeError) as e:
                    matchCell = match['Home'] + matchCell
                try:
                    matchCell = matchCell + match['Away'] + ' ' + match['A Sprite']
                except (KeyError, TypeError) as e:
                    matchCell = matchCell + match['Away']
                if match['C Sprite'] != None:
                    compCell = match['C Sprite'] + ' ' + match['Competition']
                else:
                    compCell = match['Competition']
                temp = {
                    'time' : timestamp,
                    'match' : matchCell,
                    'comp' : compCell,
                    'round' : match['Round']
                }
                
                row = ''
                if match['Bold'] == 0:
                    for cell in temp:
                        celldata = temp[cell]
                        if celldata != None:
                            row = row + temp[cell] + ' | '
                        else:
                            row = row + '' + ' | '
                    row = row[:-2]
                    wf.write(row + '\n')
                else:
                    for cell in temp:
                        celldata = temp[cell]
                        if celldata != None:
                            row = row + '**' + temp[cell] + '** | '
                        else:
                            row = row + '' + " | "
                    row = row[:-2]
                    wf.write(row + '\n')
                    
        wf.write('\nr/WhatToWatchThisWeek')
WTWTW_main()