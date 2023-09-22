# External
import requests, logging
from bs4 import BeautifulSoup
from datetime import datetime
# Internal
from astrobot.core.astrology import ZodiacSign
from astrobot.modules.horoscope import Source, Style
from astrobot.modules.sources.common import Day, Source, Style, HoroSource


class HoroscopeCom(HoroSource):
    """Class for working with individual horoscopes from Horoscope.com.
    """
    def __init__(self, sign: ZodiacSign, day: Day, style: Style) -> None:
        """Class for working with individual horoscopes from Horoscope.com.

        Args:
            sign (ZodiacSign): Zodiac sign to fetch horoscope for.
            day (Day): Relative day to fetch horoscope for.
            style (Style): Style of horoscope to fetch.
        """
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
        """Generate URL for __fetch.

        Args:
            sign (ZodiacSign): Zodiac sign to fetch horoscope for.
            style (Style): Relative day to fetch horoscope for.
            day (Day): Style of horoscope to fetch.

        Returns:
            str: The URL to fetch from.
        """
        url_base: str                       = "https://www.horoscope.com/us/horoscopes/"
        style_text: dict[Style, str]        = {Style.daily:       "general/horoscope-general-daily-",
                                               Style.daily_love:  "love/horoscope-love-daily-"}
        horo_day: dict[Day, str]            = {Day.tomorrow:  "tomorrow.aspx",
                                               Day.today:     "today.aspx",
                                               Day.yesterday: "yesterday.aspx"}
        sign_number: dict[ZodiacSign, str]  = {ZodiacSign.aries:       "?sign=1",
                                               ZodiacSign.taurus:      "?sign=2",
                                               ZodiacSign.gemini:      "?sign=3",
                                               ZodiacSign.cancer:      "?sign=4",
                                               ZodiacSign.leo:         "?sign=5",
                                               ZodiacSign.virgo:       "?sign=6",
                                               ZodiacSign.libra:       "?sign=7",
                                               ZodiacSign.scorpio:     "?sign=8",
                                               ZodiacSign.sagittarius: "?sign=9",
                                               ZodiacSign.capricorn:   "?sign=10",
                                               ZodiacSign.aquarius:    "?sign=11",
                                               ZodiacSign.pisces:      "?sign=12"}
        url_return: list[str]               = [url_base, style_text[style], horo_day[day], sign_number[sign]]
        return "".join(url_return)
    
    def __restore_split(self, split: list[str]) -> list:
        """Fix splitting on dashes, they're sometimes used in the content text.

        Args:
            split (list[str]): The list to fix.

        Returns:
            list: The fixed list.
        """
        length: int     = len(split)
        new: list[str]  = []

        for i in range(length):
            if ( i == (length - 1) ):
                new.append(split[i])
            else:
                new.append(split[i])
                new.append(" - ")
        
        return new
    
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
            soup: BeautifulSoup     = BeautifulSoup(req.text, "html.parser")
            
            content_list: list[str] = soup.find("div", class_="main-horoscope").find("p").text.split(" - ")[1:] # type: ignore
            new                     = self.__restore_split(split=content_list)
            content                 = "".join(new)
            
            date_rough              = soup.find("div", class_="main-horoscope").find("strong").text.strip() # type: ignore
            date_dt: datetime       = datetime.strptime(date_rough, "%b %d, %Y")
            date: str               = date_dt.strftime("%B %d, %Y")
            
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
        add: dict       = {}

        add = {"name": Source.horoscope_com.full, "styles": {}}
        d.update(add)
        for style in Source.horoscope_com.styles:
            add         = {style.name: {"name": style.full, "days": {}}}
            d["styles"].update(add)
            for day in Day:
                add     = {day.name: {"date": "", "signs": {}}}
                d["styles"][style.name]["days"].update(add)
                for sign in ZodiacSign:
                    add = {sign.name: ""}
                    d["styles"][style.name]["days"][day.name]["signs"].update(add)
        
        return d