import requests, json
from os import path, getenv
from dotenv import load_dotenv

load_dotenv()
FILE = getenv('DATAFILE')
urlBase = "https://ohmanda.com/api/horoscope/"
data = {"signs" : {}}
data["signs"] = {"aries" : {},\
    "taurus" : {},\
    "gemini" : {},\
    "cancer" : {},\
    "leo" : {},\
    "virgo" : {},\
    "libra" : {},\
    "scorpio" : {},\
    "sagittarius" : {},\
    "capricorn" : {},\
    "aquarius" : {},\
    "pisces" : {}\
    }

def updateHoro(file):
    for s in data["signs"]:
        req = requests.get(urlBase + s + "/")
        d = json.loads(req.text)
        data["signs"][s]["date"] = d["date"]
        data["signs"][s]["horoscope"] = d["horoscope"]

    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def checkData(file):
    if path.exists(file):
        return True
    else:
        return False

def loadData(file):
    d = {}
    if checkData(file):
        with open(file, "r", encoding="utf-8") as f:
            d = json.load(f)
    else:
        print("Updating data...")
        updateHoro(file)
        with open(file, "r", encoding="utf-8") as f:
            d = json.load(f)
    return d
        
def getHoro(sign, file):
    d = loadData(file)
    return d["signs"][sign]
