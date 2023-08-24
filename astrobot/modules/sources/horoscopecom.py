# External
import requests, logging
from datetime import datetime
from bs4 import BeautifulSoup
# Internal
from astrobot.core.datatypes import Day, Source, Style, Zodiac


class HoroscopeCom:
    '''Class for working with individual horoscopes from Horoscope.com'''
    def __init__(self, zodiac: Zodiac.Type, day: Day.Type, style: Style.Type) -> None:
        '''Class for working with individual horoscopes from Horoscope.com
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
        '''Creates empty data structure for Horoscope.com data, should be called from __create_data(), returns dict'''
        d: dict = {}
        add: dict = {}

        add = {"name": Source.horoscope_com.full, "styles": {}}
        d.update(add)
        for style in Source.horoscope_com.styles:
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
        url_base: str = "https://www.horoscope.com/us/horoscopes/"

        style_text: dict[Style.Type, str] = {Style.daily:       "general/horoscope-general-daily-",
                                             Style.daily_love:  "love/horoscope-love-daily-"}

        horo_day: dict[Day.Type, str] = {Day.tomorrow:  "tomorrow.aspx",
                                         Day.today:     "today.aspx",
                                         Day.yesterday: "yesterday.aspx"}
        
        sign_number: dict[Zodiac.Type, str] = {Zodiac.aries:       "?sign=1",
                                               Zodiac.taurus:      "?sign=2",
                                               Zodiac.gemini:      "?sign=3",
                                               Zodiac.cancer:      "?sign=4",
                                               Zodiac.leo:         "?sign=5",
                                               Zodiac.virgo:       "?sign=6",
                                               Zodiac.libra:       "?sign=7",
                                               Zodiac.scorpio:     "?sign=8",
                                               Zodiac.sagittarius: "?sign=9",
                                               Zodiac.capricorn:   "?sign=10",
                                               Zodiac.aquarius:    "?sign=11",
                                               Zodiac.pisces:      "?sign=12"}

        url_return: list[str] = [url_base, style_text[style], horo_day[day], sign_number[zodiac]]
        return "".join(url_return)
    
    @staticmethod
    def __restore_split(split: list[str]) -> list:
        length: int = len(split)
        new: list[str] = []

        for i in range(length):
            if ( i == (length - 1) ):
                new.append(split[i])
            else:
                new.append(split[i])
                new.append(" - ")
        
        return new
    
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
            
            content_list: list[str] = soup.find("div", class_="main-horoscope").find("p").text.split(" - ")[1:] # type: ignore
            new = self.__restore_split(split=content_list)
            content = "".join(new)
            
            date_rough = soup.find("div", class_="main-horoscope").find("strong").text.strip() # type: ignore
            date_dt: datetime = datetime.strptime(date_rough, "%b %d, %Y")
            date: str = date_dt.strftime("%B %d, %Y")
            
            return date, content
        else:
            return "", ""