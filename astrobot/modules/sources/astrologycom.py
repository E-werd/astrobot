# External
import requests, logging
from bs4 import BeautifulSoup
# Internal
from astrobot.core.astrology import ZodiacSign
from astrobot.modules.horoscope import Source, Style
from astrobot.modules.sources.common import Day, Source, Style, HoroSource


class AstrologyCom(HoroSource):
    """Class for working with individual horoscopes from Astrology.com.
    """
    def __init__(self, sign: ZodiacSign, day: Day, style: Style) -> None:
        """Class for working with individual horoscopes from Astrology.com.

        Args:
            sign (ZodiacSign): Zodiac sign to fetch horoscope for.
            day (Day): Relative day to fetch horoscope for.
            style (Style): Style of horoscope to fetch.
        """
        self.__url: str     = self.__get_url(sign=sign, style=style, day=day)
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
        """Generate URL for __fetch.

        Args:
            sign (ZodiacSign): Zodiac sign to fetch horoscope for.
            style (Style): Relative day to fetch horoscope for.
            day (Day): Style of horoscope to fetch.

        Returns:
            str: The URL to fetch from.
        """
        url_return: list[str]               = ["https://www.astrology.com/"]
        style_text: dict[Style, str]        = {Style.daily:       "horoscope/daily/",
                                               Style.daily_love:  "horoscope/daily-love/"}
        day_text: dict[Day, str]            = {Day.yesterday: f"{day.name}/{sign.name}.html",
                                               Day.tomorrow:  f"{day.name}/{sign.name}.html",
                                               Day.today:     f"{sign.name}.html"}
        
        url_return += [style_text[style], day_text[day]]
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
            content             = soup.find(id="content").find_all("span") # type: ignore
            date: str           = soup.find(id="content-date").text # type: ignore
            return date, "".join(s.text for s in content)
        else:
            return "", ""
        
    @staticmethod
    def create_source_structure() -> dict:
        """Creates empty data structure for source data. Should be called from __create_data().

        Returns:
            dict: Dict containing empty data structure.
        """
        d: dict             = {}
        add: dict           = {"name": Source.astrology_com.full, "styles": {}}
        d.update(add)
        for style in Source.astrology_com.styles:
            add             = {style.name: {"name": style.full, "days": {}}}
            d["styles"].update(add)
            for day in Day:
                add         = {day.name: {"date": "", "signs": {}}}
                d["styles"][style.name]["days"].update(add)
                for sign in ZodiacSign:
                    add     = {sign.name: ""}
                    d["styles"][style.name]["days"][day.name]["signs"].update(add)
        
        return d