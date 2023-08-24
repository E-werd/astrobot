# External
import requests, logging
from bs4 import BeautifulSoup
# Internal
from astrobot.core.datatypes import Day, Source, Style, Zodiac


class Astrostyle:
    '''Class for working with individual horoscopes from Astrostyle.com'''
    def __init__(self, zodiac: Zodiac.Type, day: Day.Type, style: Style.Type) -> None:
        '''Class for working with individual horoscopes from Astrostyle.com
        :zodiac: Zodiac sign
        :day: Day for horoscope. Day.Type object, enumerated in Day.types
        :style: Horoscope style. Style.Type object, enumerated in Style.types'''
        self.day: Day.Type = day
        self.__url: str = self.__get_url(zodiac=zodiac, style=style, day=self.day)
        self.date: str = ""
        self.text: str = ""

        for i in range(3):
            logging.debug(f"Fetch attempt {i + 1} of 3...")
            date, text = self.__fetch(url=self.__url)
            if (text == ""): 
                logging.debug(f"Bad fetch.")
                continue
            logging.debug(f"Good fetch.")
            self.date = date
            self.text = text
            break

    @staticmethod
    def create_source_structure() -> dict:
        '''Creates empty data structure for AstroStyle data, should be called from __create_data(), returns dict'''
        d: dict = {}
        add: dict = {}

        add = {"name": Source.astrostyle.full, "styles": {}}
        d.update(add)
        for style in Source.astrostyle.styles:
            add = {style.name: {"name": style.full, "emoji": style.symbol, "days": {}}}
            d["styles"].update(add)
            for day in Day.types:
                add = {day: {"date": "", "emoji": Day.types[day].symbol, "signs": {}}}
                d["styles"][style.name]["days"].update(add)
                for zodiac in Zodiac.types:
                    add = {zodiac: ""}
                    d["styles"][style.name]["days"][day]["signs"].update(add)
        
        return d

    def __get_url(self, zodiac: Zodiac.Type, style: Style.Type, day: Day.Type) -> str:
        '''Generate url for __fetch, returns str
        :zodiac: Zodiac sign
        :style: Horoscope style
        :day: Day for horoscope'''
        url_return: list[str] = ["https://astrostyle.com/"]

        dayname: str = ""
        match day.day_of_week:
                            case "saturday" | "sunday":
                                dayname = "weekend"
                            case _:
                                dayname = day.day_of_week

        url_return += ["horoscopes/daily/", zodiac.name, "/", dayname, "/"]
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
            content = soup.find("div", class_="horoscope-content").find("p").text.strip() # type: ignore
            date: str = soup.find("div", class_="horoscope-content").find("h2").text.split("Horoscope for")[1].strip() # type: ignore
            return date, content
        else:
            return "", ""