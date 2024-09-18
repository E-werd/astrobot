# External
import logging, asyncio
import time as timer
from abc import ABC
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, time
from aiohttp_client_cache import CachedSession, SQLiteBackend # type: ignore
from aiohttp_client_cache.response import CachedResponse
# Internal
from astrobot.core.common import Misc
from astrobot.core.astrology import ZodiacSign
from astrobot.modules.common import Day, Source, Style


class CacheStatus:
    def __init__(self, cached: bool, expires: datetime) -> None:
        self.is_cached: bool    = cached
        self.expires: datetime  = expires

class Horo:
    """Container class for individual horoscopes.
    """
    def __init__(self,
                 cache: CacheStatus,
                 sign: ZodiacSign, 
                 date: str, 
                 text: str              = "",
                 url: str               = "",
                 source: Source         = Source.astrology_com, 
                 style: Style           = Style.daily
                 ) -> None:
        """Container class for individual horoscopes. Served by Horoscope object with get_horoscope().

        Args:
            sign (ZodiacSign): Zodiac sign.
            date (str): Formatted date string, use a function from Misc to generate.
            text (str, optional): Horoscope text. Defaults to "".
            source (Source, optional): Source of horoscope. Defaults to Source.astrology_com.
            style (Style, optional): Style of horoscope. Defaults to Style.daily.
        """
        self.cache: CacheStatus     = cache
        self.sign: ZodiacSign       = sign
        self.date: str              = date
        self.text: str              = text
        self.url: str               = url
        self.source: Source         = source
        
        if style not in source.styles:
            self.style = source.default_style
        else:
            self.style = style

    def get_formatted_string(self) -> str:
        # Format data into a list
        day_of_week: str        = Misc.get_day_of_week_from_string(string=self.date).capitalize() + ","
        _day: Day               = Misc.get_day(date=self.date)
        header: list[str]       = ["### ", 
                                   self.sign.symbol, self.sign.full, 
                                   self.style.symbol, self.style.full, 
                                   "for", _day.symbol, 
                                   day_of_week, self.date,
                                   "from", f"[{self.source.full}](<{self.url}>)"]
        body: str               = self.text

        # Put data into single string, send
        return " ".join(header) + "\n" + body

class Get(ABC):
    async def get(self, url: str = "") -> CachedResponse:
        fetch: str = ""

        if url == "":
            fetch = self.url # type: ignore
        else:
            fetch = url

        try: 
            logging.debug(f"Querying URL: {fetch}")

            async with CachedSession(cache=SQLiteBackend(cache_name='astrobot_cache', urls_expire_after=self.urls_expire_after)) as session: # type: ignore
                response: CachedResponse = await CachedResponse.from_client_response(await session.get(url=fetch))

            return response

        except Exception as e: 
            logging.error(f"*** Query error: {str(e)}")
            return response # type: ignore

class UrlBuilder(ABC):
    def build_url(self, day: Day, source: Source, style: Style, sign: ZodiacSign) -> str:
        baseurl: dict[Source, str]              = {Source.astrology_com: "https://www.astrology.com/",
                                                   Source.astrostyle: "https://astrostyle.com/",
                                                   Source.horoscope_com: "https://www.horoscope.com/us/horoscopes/"}
        url_return: list[str]                   = [baseurl[source]]

        if source == Source.astrology_com:
            style_text: dict[Style, str]        = {Style.daily:       "horoscope/daily/",
                                                   Style.daily_love:  "horoscope/daily-love/"}
            day_text: dict[Day, str]            = {Day.yesterday: f"{day.name}/{sign.name}.html",
                                                   Day.tomorrow:  f"{day.name}/{sign.name}.html",
                                                   Day.today:     f"{sign.name}.html"}
            url_return                          += [style_text[style], day_text[day]]
            return "".join(url_return)
        
        elif source == Source.astrostyle:
            days: dict[str, str]                = {"sunday"    : "weekend",
                                                   "monday"    : "monday",
                                                   "tuesday"   : "tuesday",
                                                   "wednesday" : "wednesday",
                                                   "thursday"  : "thursday",
                                                   "friday"    : "friday",
                                                   "saturday"  : "weekend"}
            day_of_week: str                    = Misc.get_day_of_week_from_day(day=day)
            url_return                          += ["horoscopes/daily/", sign.name, "/", days[day_of_week], "/"]
            return "".join(url_return)
        
        elif source == Source.horoscope_com:
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
            url_return                          += [style_text[style], horo_day[day], sign_number[sign]]
            return "".join(url_return)
        else:
            return "" # This shouldn't happen.

class HoroParser(ABC):
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

    def parse_response(self, source: Source, day: Day, text: str) -> tuple[str, str]:
        parser: str = "html.parser" # BS4 parser engine

        if source == Source.astrology_com:
            soup: BeautifulSoup = BeautifulSoup(text, parser)
            content             = soup.find(id="content").find_all("span") # type: ignore
            date: str           = soup.find(id="content-date").text # type: ignore
            return date, "".join(s.text for s in content)
        elif source == Source.astrostyle:
            soup: BeautifulSoup     = BeautifulSoup(text, parser)
            content                 = soup.find("div", class_="horoscope-content").find("p").text.strip() # type: ignore
            
            date: str               = ""
            day_of_week: str        = Misc.get_day_of_week_from_day(day=day)
 
            if (day_of_week == "saturday"):
                date                = soup.find("div", class_="horoscope-content").find("h2").text.split("Horoscope for")[1].split(" - ")[0].strip() # type: ignore
            elif (day_of_week == "sunday"):
                date                = soup.find("div", class_="horoscope-content").find("h2").text.split("Horoscope for")[1].split(" - ")[1].strip() # type: ignore
            else:
                date                = soup.find("div", class_="horoscope-content").find("h2").text.split("Horoscope for")[1].strip() # type: ignore
            
            return date, content
        elif source == Source.horoscope_com:
            soup: BeautifulSoup     = BeautifulSoup(text, parser)
            
            content_list: list[str] = soup.find("div", class_="main-horoscope").find("p").text.split(" - ")[1:] # type: ignore
            new                     = self.__restore_split(split=content_list)
            content                 = "".join(new)
            
            date_rough              = soup.find("div", class_="main-horoscope").find("strong").text.strip() # type: ignore
            date_dt: datetime       = datetime.strptime(date_rough, "%b %d, %Y")
            date: str               = date_dt.strftime("%B %d, %Y")
            
            return date, content
        else:
            return "", ""

class HoroItem(Get, UrlBuilder, HoroParser):
    def __init__(self, day: Day, source: Source, style: Style, sign: ZodiacSign) -> None:
        self.day: Day                   = day
        self.source: Source             = source
        self.style: Style               = style
        self.sign: ZodiacSign           = sign
        self.date: str                  = ""
        self.text: str                  = ""
        self.url: str                   = self.build_url(day=self.day, 
                                                         source=self.source, 
                                                         style=self.style, 
                                                         sign=self.sign)
        self.urls_expire_after: dict    = {self.url: self.__get_expiration_datetime(hour=3, minute=5)}

    def __get_expiration_datetime(self, hour: int = 0, minute: int = 0) -> datetime:
        today: datetime     = datetime.combine(date=datetime.today(), time=time(hour=hour, minute=minute))
        tomorrow: datetime  = today + timedelta(days=1)

        if datetime.now().time() > today.time():
            return tomorrow
        else:
            return today

    async def fetch(self) -> Horo:
        response: CachedResponse    = await self.get(url=self.url)

        if response.expires != None:
            cache = CacheStatus(cached=True, expires=response.expires) # type: ignore
        else:
            cache = CacheStatus(cached=False, expires=datetime.now())

        text = await response.text()
        self.date, self.text        = self.parse_response(source=self.source, day=self.day, text=text)
        
        return Horo(cache=cache, sign=self.sign, date=self.date, text=self.text, url=self.url, source=self.source, style=self.style)
    
    @staticmethod
    async def __list_all() -> list:
        horoscopes: list[HoroItem] = []

        for day in Day:
            for source in Source:
                for style in source.styles:
                    for sign in ZodiacSign:
                        horo = HoroItem(day=day, source=source, style=style, sign=sign)
                        horoscopes.append(horo)

        return horoscopes
    
    @staticmethod
    async def precache() -> None:
        logging.info("Precaching all possible horoscopes...")
        tic = timer.perf_counter()

        responses = []
        horoscopes: list[HoroItem] = await HoroItem.__list_all()
        for horo in horoscopes:
            responses.append(horo.get())
        await asyncio.gather(*responses)

        toc = timer.perf_counter()
        logging.info(f"Precaching completed! {toc - tic:0.3f}s")

    @staticmethod
    async def get_all() -> list:
        await HoroItem.precache()

        logging.info("Processing all horoscope responses...")
        tic = timer.perf_counter()

        tasks = []
        horocopes: list[HoroItem] = await HoroItem.__list_all()

        for horo in horocopes:
            tasks.append(horo.fetch())
        horos: list[Horo] = await asyncio.gather(*tasks)

        toc = timer.perf_counter()
        logging.info(f"Processing completed! {toc - tic:0.3f}s")

        return horos