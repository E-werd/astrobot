# External
import requests, logging
from bs4 import BeautifulSoup
# Internal
from datatypes import Day, Source, Style, Zodiac

class AstrologyCom:
    '''Class for working with individual horoscopes from Astrology.com'''
    def __init__(self, zodiac: Zodiac.Type, day: Day.Type, style: Style.Type) -> None:
        '''Class for working with individual horoscopes from Astrology.com
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
        '''Creates empty data structure for Astrology.com data, should be called from __create_data(), returns dict'''
        d: dict = {}
        add: dict = {}

        add = {"name": Source.astrology_com.full, "styles": {}}
        d.update(add)
        for style in Source.astrology_com.styles:
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
        url_return: list[str] = ["https://www.astrology.com/"]

        match style:
            case Style.daily:
                match day:
                    case Day.yesterday | Day.tomorrow:
                        url_return += ["horoscope/daily/", day.name, "/", zodiac.name, ".html"]
                        return "".join(url_return)
                    case Day.today:
                        url_return += ["horoscope/daily/", zodiac.name, ".html"]
                        return "".join(url_return)
                    case _: return "" # This should never happen
            case Style.daily_love:
                match day:
                    case Day.yesterday | Day.tomorrow:
                        url_return += ["horoscope/daily-love/", day.name, "/", zodiac.name, ".html"]
                        return "".join(url_return)
                    case Day.today:
                        url_return += ["horoscope/daily-love/", zodiac.name, ".html"]
                        return "".join(url_return)
                    case _: return "" # This should never happen
            case _: return "" # This should never happen
    
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

        soup: BeautifulSoup = BeautifulSoup(req.text, "html.parser")
        content = soup.find(id="content").find_all("span") # type: ignore
        date: str = soup.find(id="content-date").text # type: ignore
        return date, "".join(s.text for s in content)