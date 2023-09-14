# External
import requests, logging
from bs4 import BeautifulSoup
# Internal
from astrobot.core.datatypes import Day, Source, Style, ZodiacSign


class AstrologyCom:
    '''Class for working with individual horoscopes from Astrology.com'''
    def __init__(self, sign: ZodiacSign, day: Day, style: Style) -> None:
        '''Class for working with individual horoscopes from Astrology.com
        :sign: Zodiac sign
        :day: Day for horoscope.
        :style: Horoscope style.'''
        self.day: Day       = day
        self.__url: str     = self.__get_url(sign=sign, style=style, day=self.day)
        self.date: str      = ""
        self.text: str      = ""

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
        url_return: list[str]               = ["https://www.astrology.com/"]
        style_text: dict[Style, str]        = {Style.daily:       "horoscope/daily/",
                                               Style.daily_love:  "horoscope/daily-love/"}
        day_text: dict[Day, str]            = {Day.yesterday: f"{day.name}/{sign.name}.html",
                                               Day.tomorrow:  f"{day.name}/{sign.name}.html",
                                               Day.today:     f"{sign.name}.html"}
        
        url_return += [style_text[style], day_text[day]]
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
            content             = soup.find(id="content").find_all("span") # type: ignore
            date: str           = soup.find(id="content-date").text # type: ignore
            return date, "".join(s.text for s in content)
        else:
            return "", ""
        
    @staticmethod
    def create_source_structure() -> dict:
        '''Creates empty data structure for Astrology.com data, should be called from __create_data(), returns dict'''
        d: dict             = {}
        add: dict           = {"name": Source.astrology_com.full, "styles": {}}
        d.update(add)
        for style in Source.astrology_com.styles:
            add             = {style.name: {"name": style.full, "emoji": style.symbol, "days": {}}}
            d["styles"].update(add)
            for day in Day:
                add         = {day.name: {"date": "", "emoji": day.symbol, "signs": {}}}
                d["styles"][style.name]["days"].update(add)
                for sign in ZodiacSign:
                    add     = {sign.name: ""}
                    d["styles"][style.name]["days"][day.name]["signs"].update(add)
        
        return d