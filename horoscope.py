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
        j = json.loads(req.text)
        data["signs"][s]["date"] = j["date"]
        data["signs"][s]["horoscope"] = j["horoscope"]

    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

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
        
def getHoro(sign, f):
    d = loadData(f)
    return d["signs"][sign]
