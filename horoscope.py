import requests, json
from os import path
from bs4 import BeautifulSoup

urlBase = "https://www.astrology.com/horoscope/"
signs = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
data = {"signs": {}}

for sign in signs:
    data["signs"][sign] = {}
    data["signs"][sign]["name"] = str(sign).capitalize()
    data["signs"][sign]["yesterday"] = {"date": "", "horoscope": ""}
    data["signs"][sign]["today"] = {"date": "", "horoscope": ""}
    data["signs"][sign]["tomorrow"] = {"date": "", "horoscope": ""}

def scrapeData(sign: str, when: str, url: str):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    content = soup.find(id="content")

    data["signs"][sign][when]["date"] = soup.find(id="content-date").text  # type: ignore
    data["signs"][sign][when]["horoscope"] = content.find("span").text.strip() # type: ignore

def updateHoro(file: str):
    for sign in data["signs"]:
        today = urlBase + "daily/" + sign + ".html"
        tomorrow = urlBase + "daily/tomorrow/" + sign + ".html"
        yesterday = urlBase + "daily/yesterday/" + sign + ".html"

        print("Fetching " + sign + ":today from: " + today)
        scrapeData(sign=sign, url=today, when="today")
        print("Fetching " + sign + ":tomorrow from: " + tomorrow)
        scrapeData(sign=sign, url=tomorrow, when="tomorrow")
        print("Fetching " + sign + ":yesterday from: " + yesterday)
        scrapeData(sign=sign, url=yesterday, when="yesterday")

    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def checkData(file: str):
    if path.exists(file):
        return True
    else:
        return False

def loadData(file: str):
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
        
def getHoro(sign: str, file: str):
    d = loadData(file)
    return d["signs"][sign]