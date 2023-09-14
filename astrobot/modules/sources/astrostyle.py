# External
import requests, logging
from bs4 import BeautifulSoup
# Internal
from astrobot.core.datatypes import Day, Source, Style, ZodiacSign
from astrobot.core.misc import Misc


class Astrostyle:
    '''Class for working with individual horoscopes from Astrostyle.com'''
    def __init__(self, sign: ZodiacSign, day: Day, style: Style) -> None:
        '''Class for working with individual horoscopes from Astrostyle.com
        :sign: Zodiac sign
        :day: Day for horoscope.
        :style: Horoscope style.'''
        self.day: Day   = day
        self.__url: str = self.__get_url(sign=sign, style=style, day=self.day)
        self.date: str  = ""
        self.text: str  = ""

        for i in range(3):
            logging.debug(f"Fetch attempt {i + 1} of 3...")
            date, text  = self.__fetch(url=self.__url)
            if (text == ""): 
                logging.debug(f"Bad fetch.")
                continue
            logging.debug(f"Good fetch.")
            self.date   = date
            self.text   = text
            break

    def __get_url(self, sign: ZodiacSign, style: Style, day: Day) -> str:
        '''Generate url for __fetch, returns str
        :sign: Zodiac sign
        :style: Horoscope style
        :day: Day for horoscope'''
        url_return: list[str]   = ["https://astrostyle.com/"]
        days: dict[str, str]    = {"sunday"    : "weekend",
                                   "monday"    : "monday",
                                   "tuesday"   : "tuesday",
                                   "wednesday" : "wednesday",
                                   "thursday"  : "thursday",
                                   "friday"    : "friday",
                                   "saturday"  : "weekend"}
        day_of_week: str        = Misc.get_day_of_week_from_day(day=day)
        url_return              += ["horoscopes/daily/", sign.name, "/", day_of_week, "/"]
        return "".join(url_return)
    
    def __fetch(self, url: str) -> tuple[str, str]:
        '''Retrieve horoscope from source, returns two str: date and text
        :url: URL from which to fetch horoscope'''
        req: requests.Response

        try: 
            logging.debug(f"Fetching from url: {url}")
            req = requests.get(url=url, timeout=(5, 10)) # 5s connection, 10s request
        except Exception as e: 
            logging.error(f"*** Fetch error: {str(e)}")
            return "", ""

        if (req.status_code == 200):
            soup: BeautifulSoup = BeautifulSoup(req.text, "html.parser")
            content             = soup.find("div", class_="horoscope-content").find("p").text.strip() # type: ignore
            
            date: str           = ""
            day_of_week: str    = Misc.get_day_of_week_from_day(day=self.day)
            match day_of_week:
                case "saturday":
                    date        = soup.find("div", class_="horoscope-content").find("h2").text.split("Horoscope for")[1].split(" - ")[0].strip() # type: ignore
                case "sunday":
                    date        = soup.find("div", class_="horoscope-content").find("h2").text.split("Horoscope for")[1].split(" - ")[1].strip() # type: ignore
                case _:
                    date        = soup.find("div", class_="horoscope-content").find("h2").text.split("Horoscope for")[1].strip() # type: ignore

            return date, content
        else:
            return "", ""
        
    @staticmethod
    def create_source_structure() -> dict:
        '''Creates empty data structure for AstroStyle data, should be called from __create_data(), returns dict'''
        d: dict         = {}
        add: dict       = {"name": Source.astrostyle.full, "styles": {}}
        d.update(add)
        for style in Source.astrostyle.styles:
            add         = {style.name: {"name": style.full, "emoji": style.symbol, "days": {}}}
            d["styles"].update(add)
            for day in Day:
                add     = {day.name: {"date": "", "emoji": day.symbol, "signs": {}}}
                d["styles"][style.name]["days"].update(add)
                for sign in ZodiacSign:
                    add = {sign.name: ""}
                    d["styles"][style.name]["days"][day.name]["signs"].update(add)
        
        return d