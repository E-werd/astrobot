# External
import requests, logging
from bs4 import BeautifulSoup
# Internal
from astrobot.core.common import Misc
from astrobot.core.astrology import ZodiacSign
from astrobot.modules.horoscope import Source, Style
from astrobot.modules.sources.common import Day, Source, Style, HoroSource


class Astrostyle(HoroSource):
    """Class for working with individual horoscopes from Astrostyle.com.
    """
    def __init__(self, sign: ZodiacSign, day: Day, style: Style) -> None:
        """Class for working with individual horoscopes from Astrostyle.com.

        Args:
            sign (ZodiacSign): Zodiac sign to fetch horoscope for.
            day (Day): Relative day to fetch horoscope for.
            style (Style): Style of horoscope to fetch.
        """
        self.__url: str = self.__get_url(sign=sign, style=style, day=day)
        self.__day: Day = day
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
        """Generate URL for __fetch.

        Args:
            sign (ZodiacSign): Zodiac sign to fetch horoscope for.
            style (Style): Relative day to fetch horoscope for.
            day (Day): Style of horoscope to fetch.

        Returns:
            str: The URL to fetch from.
        """
        url_return: list[str]   = ["https://astrostyle.com/"]
        days: dict[str, str]    = {"sunday"    : "weekend",
                                   "monday"    : "monday",
                                   "tuesday"   : "tuesday",
                                   "wednesday" : "wednesday",
                                   "thursday"  : "thursday",
                                   "friday"    : "friday",
                                   "saturday"  : "weekend"}
        day_of_week: str        = Misc.get_day_of_week_from_day(day=day)
        url_return              += ["horoscopes/daily/", sign.name, "/", days[day_of_week], "/"]
        return "".join(url_return)
    
    def __fetch(self, url: str) -> tuple[str, str]:
        """Fetch horoscope from source URL.

        Args:
            url (str): The URL to fetch from.

        Returns:
            tuple[str, str]: A two-element string tuple containing a date and horoscope content, respectively.
        """
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
            day_of_week: str    = Misc.get_day_of_week_from_day(day=self.__day)
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
        """Creates empty data structure for source data. Should be called from __create_data().

        Returns:
            dict: Dict containing empty data structure.
        """
        d: dict         = {}
        add: dict       = {"name": Source.astrostyle.full, "styles": {}}
        d.update(add)
        for style in Source.astrostyle.styles:
            add         = {style.name: {"name": style.full, "days": {}}}
            d["styles"].update(add)
            for day in Day:
                add     = {day.name: {"date": "", "signs": {}}}
                d["styles"][style.name]["days"].update(add)
                for sign in ZodiacSign:
                    add = {sign.name: ""}
                    d["styles"][style.name]["days"][day.name]["signs"].update(add)
        
        return d