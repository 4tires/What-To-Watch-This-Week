import difflib
import time
import csv
from typing import OrderedDict
import pprint
import json

testDict = {
    'Jedinstvo Bihac' : 'Jedinstvo Biha\u0107',
    "San Jose" : "San Jos\u00e9",
    "Real Potosi" : "Real Potos\u00ed",
    "Guabira" : "Guabir\u00e1",
    "Qarabag" : "Qaraba\u011f",
    "Luftetari Gjirokastra" : "Luft\u00ebtari Gjirokast\u00ebr",
    "Gabala" : "Q\u0259b\u0259l\u0259",
    "Bronshoj" : "Br\u00f8nsh\u00f8j BK",
    "Ryukyu" : "FC Ry\u016bky\u016b",
    "Decic" : "De\u010di\u0107 Tuzi",
    "Vitoria Guimaraes" : "Vit\u00f3ria de Guimar\u00e3es",
    "Vasteras SK" : "V\u00e4ster\u00e5s SK",
    "Besiktas" : "Be\u015fikta\u015f",
    "Genclerbirligi" : "Gen\u00e7lerbirli\u011fi",
    "Karsiyaka" : "Kar\u015f\u0131yaka",
    "Kasimpasa" : "Kas\u0131mpa\u015fa",

    'one' : 'ONE'
}
for key, value in testDict.items():
    score = difflib.SequenceMatcher(None, key, value).ratio()
    print(key, value, ':', round(score, 4), score)
