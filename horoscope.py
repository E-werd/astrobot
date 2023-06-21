import requests, json, logging
from os import path
from bs4 import BeautifulSoup

urlBase = "https://www.astrology.com/"
urlDaily = urlBase + "horoscope/daily/"
urlDailyLove = urlBase + "horoscope/daily-love/"
signs = ["aries", "taurus", "gemini", "cancer", "leo", "virgo", "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces"]
styles = ["daily", "daily-love"]
days = ["yesterday", "today", "tomorrow"]
data = {"signs": {}}

for sign in signs:
    data["signs"][sign] = {}
    data["signs"][sign]["name"] = str(sign).capitalize()
    for style in styles:
        data["signs"][sign][style] = {}
        for day in days:
            data["signs"][sign][style][day] = {}
            data["signs"][sign][style][day] = {"date": "", "horoscope": ""}

def scrapeData(sign: str, day: str, style: str):
    url = ""
    match style:
        case "daily":
            url = urlDaily + day + "/" + sign + ".html"
        case "daily-love":
            match day:
                case "yesterday" | "tomorrow":
                    url = urlDailyLove + day + "/" + sign + ".html"
                case "today":
                    url = urlDailyLove + sign + ".html"

    req = requests.get(url)
    soup = BeautifulSoup(req.text, "html.parser")
    content = soup.find(id="content")

    data["signs"][sign][style][day]["date"] = soup.find(id="content-date").text  # type: ignore

    span = content.find_all("span") # type: ignore
    horo = ""
    for s in span:
        horo += s.text
    data["signs"][sign][style][day]["horoscope"] = horo # type: ignore

def updateHoro(file: str):
    for sign in signs:
        for style in styles:
            for day in days:
                logging.debug("Fetching " + style + " for " + sign + ":" + day)
                scrapeData(sign=sign, style=style, day=day)

    logging.info("Writing data to file: " + file)
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return True

def checkData(file: str):
    if path.exists(file):
        return True
    else:
        return False
    
def preloadData(file: str):
    if checkData(file=file):
        logging.info("Data is good at: " + file)
        return True
    else:
        logging.info("Data missing or incomplete.")
        logging.info("Updating data...")
        return updateHoro(file=file)

def loadData(file: str):
    d = {}
    if checkData(file=file):
        logging.info("Loading data from: " + file)
        with open(file, "r", encoding="utf-8") as f:
            d = json.load(f)
    else:
        logging.info("Updating data...")
        updateHoro(file=file)
        with open(file, "r", encoding="utf-8") as f:
            d = json.load(f)
    return d
        
def getHoro(sign: str, file: str):
    d = loadData(file=file)
    return d["signs"][sign]