# External
from datetime import datetime, timedelta


class Day:
    '''Class to hold possible relative days: yesterday, today, tomorrow. Use 'types' for iteration.'''
    class Type:
        def __init__(self, name: str, symbol: str) -> None:
            '''Container class for individual days
            :name: name
            :full: pretty name
            :symbol: symbol or emoji'''
            self.name: str          = name
            self.full: str          = self.name.capitalize()
            self.symbol: str        = symbol
            self.date: datetime     = self.__get_date(day=name)
            self.ymd: str           = self.date.strftime("%B %d, %Y")
            self.day_of_week: str   = self.date.strftime("%A").lower()

        def __get_date(self, day: str) -> datetime:
            '''Get date from relative day str, returns datetime
            :day: relative day name'''
            today: datetime         = datetime.today()
            offset: dict[str, int]  = {"yesterday": -1,
                                       "today"    : 0,
                                       "tomorrow" : 1}

            return today + timedelta(days=offset[day])
        
        def update(self) -> None:
            '''Update date, ymd, day_of_week for Day.Type object'''
            self.date               = self.__get_date(day=self.name)
            self.ymd: str           = self.date.strftime("%B %d, %Y")
            self.day_of_week: str   = self.date.strftime("%A").lower()

    @staticmethod    
    def update() -> None:
        '''Update date, ymd, day_of_week for all Day.Type objects'''
        for _, day in Day.types.items():
            day.update()

    yesterday: Type         = Type(name="yesterday", symbol="⏮️")
    today: Type             = Type(name="today", symbol="▶️")
    tomorrow: Type          = Type(name="tomorrow", symbol="⏭️")
    types: dict[str, Type]  = {"yesterday": yesterday, "today": today, "tomorrow": tomorrow}

class Style:
    '''Class to hold possible styles: daily, daily_love. Use 'types' for iteration.'''
    class Type:
        def __init__(self, name: str, full: str, symbol: str) -> None:
            '''Container class for individual styles
            :name: name
            :full: pretty name
            :symbol: symbol or emoji'''
            self.name: str      = name
            self.full: str      = full
            self.symbol: str    = symbol

    daily: Type             = Type(name="daily", full="Daily Horoscope", symbol="🌅")
    daily_love: Type        = Type(name="daily-love", full="Daily Love Horoscope", symbol="💗")
    types: dict[str, Type]  = {"daily": daily, "daily-love": daily_love}

class Source:
    '''Class to hold possible sources: astrology_com. Use 'types' for iteration.'''
    class Type:
        def __init__(self, name: str, full: str, styles: list, default_style: Style.Type = Style.daily) -> None:
            '''
            Container class for individual sources
            :name: name
            :full: pretty name
            '''
            self.name: str                  = name
            self.full: str                  = full
            self.styles: list[Style.Type]   = styles
            self.default_style: Style.Type  = default_style

    horoscope_com: Type     = Type(name="horoscope_com", full="Horoscope.com", styles=[Style.daily, Style.daily_love])
    astrology_com: Type     = Type(name="astrology_com", full="Astrology.com", styles=[Style.daily, Style.daily_love])
    astrostyle: Type        = Type(name="astrostyle", full="AstroStyle.com", styles=[Style.daily])
    types: dict[str, Type]  = {"astrology_com": astrology_com, "astrostyle": astrostyle, "horoscope_com": horoscope_com}

class Zodiac:
    '''Static class for describing the Zodiac: aries, ..., pisces. Use 'types' for iteration.'''
    class Type:
        def __init__(self, name: str, full: str, symbol: str) -> None:
            '''Container class for individual Zodiac Types
            :name: Zodiac Type name
            :full: Zodiac Type pretty name
            :symbol: symbol or emoji'''
            self.name: str      = name
            self.full: str      = full
            self.symbol: str    = symbol

        def __str__(self) -> str:
            return self.name
    
    aries: Type             = Type(name="aries", full="Aries", symbol="♈")
    taurus: Type            = Type(name="taurus", full="Taurus", symbol="♉")
    gemini: Type            = Type(name="gemini", full="Gemini", symbol="♊")
    cancer: Type            = Type(name="cancer", full="Cancer", symbol="♋")
    leo: Type               = Type(name="leo", full="Leo", symbol="♌")
    virgo: Type             = Type(name="virgo", full="Virgo", symbol="♍")
    libra: Type             = Type(name="libra", full="Libra", symbol="♎")
    scorpio: Type           = Type(name="scorpio", full="Scorpio", symbol="♏")
    sagittarius: Type       = Type(name="sagittarius", full="Sagittarius", symbol="♐")
    capricorn: Type         = Type(name="capricorn", full="Capricorn", symbol="♑")
    aquarius: Type          = Type(name="aquarius", full="Aquarius", symbol="♒")
    pisces: Type            = Type(name="pisces", full="Pisces", symbol="♓")
    types: dict[str, Type]  = {"aries": aries, 
                               "taurus": taurus,
                               "gemini": gemini,
                               "cancer": cancer,
                               "leo" : leo,
                               "virgo": virgo,
                               "libra": libra,
                               "scorpio": scorpio,
                               "sagittarius": sagittarius,
                               "capricorn": capricorn,
                               "aquarius": aquarius,
                               "pisces": pisces}

class Horo:
    '''Container class for individual horoscopes.'''
    def __init__(self, 
                 zodiac: Zodiac.Type, 
                 date: str, 
                 text: str = "",
                 source: Source.Type = Source.astrology_com, 
                 style: Style.Type = Style.daily
                 ) -> None:
        '''Container class for individual horoscopes. Served by Horoscope object with get_horoscope().
        :zodiac: Zodiac Sign, type: Zodiac.Type
        :day: Day of horoscope, type: Day.Type
        :text: Horoscope text, type: str
        :source: Source of horoscope. Default: Source.astrology_com
        :style: Style of horoscope, specific to Source.astrology_com. Unused if the source doesn't match. Default: AstrologyCom.Style.daily'''
        self.zodiac: Zodiac.Type    = zodiac
        self.date: str              = date
        self.text: str              = text
        self.source: Source.Type    = source
        
        if style not in source.styles:
            self.style = source.default_style
        else:
            self.style = style