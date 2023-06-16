import requests, json
from os import path
from bs4 import BeautifulSoup

urlBase = "https://www.astrology.com/horoscope/daily/"
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
        req = requests.get(urlBase + s + ".html")
        soup = BeautifulSoup(req.text, "html.parser")
        content = soup.find(id="content")

        data["signs"][s]["name"] = str(s).capitalize()
        data["signs"][s]["date"] = soup.find(id="content-date").text
        data["signs"][s]["horoscope"] = content.find("span").text.strip()

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