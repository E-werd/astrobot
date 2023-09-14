# External
from enum import Enum

class Day(Enum):
    """Enum for relative days. Value is the day offset from today.
    """
    yesterday   = -1
    today       = 0
    tomorrow    = 1

    @property
    def symbol(self) -> str:
        """Emoji symbol for the relative day.

        Returns:
            str: A UTF8 emoji symbol.
        """
        symbols: dict[str, str] = {"yesterday": "⏮️",
                                   "today":     "▶️",
                                   "tomorrow":  "⏭️"}
        return symbols[self.name]
    
    @property
    def full(self) -> str:
        """Capitalized version of the name, for presentation.

        Returns:
            str: The name of the relative day name capitalized.
        """
        return self.name.capitalize()

class Style(Enum):
    """Enum describing the possible horoscope styles.
    """
    daily       = "Daily Horoscope"
    daily_love  = "Daily Love Horoscope"

    @property
    def full(self) -> str:
        return self.value
    
    @property
    def symbol(self) -> str:
        symbols: dict[Style, str]    = {Style.daily:        "🌅",
                                        Style.daily_love:   "💗"}
        return symbols[self]

class Source(Enum):
    """Enum describing possible sources.
    """
    horoscope_com   = "Horoscope.com"
    astrology_com   = "Astrology.com"
    astrostyle      = "AstroStyle.com"

    @property
    def full(self) -> str:
        return self.value
    
    @property
    def styles(self) -> list[Style]:
        style_list: dict[Source, list[Style]]   = {Source.horoscope_com:  [Style.daily, Style.daily_love],
                                                   Source.astrology_com:  [Style.daily, Style.daily_love],
                                                   Source.astrostyle:     [Style.daily]}
        return style_list[self]
    
    @property
    def default_style(self) -> Style:
        defaults: dict[Source, Style]           = {Source.horoscope_com:    Style.daily,
                                                   Source.astrology_com:    Style.daily,
                                                   Source.astrostyle:       Style.daily}
        return defaults[self]


class ZodiacSign(Enum):
    """Enum for describing the Zodiac signs: aries, ..., pisces.
    """
    aries       = "♈"
    taurus      = "♉"
    gemini      = "♊"
    cancer      = "♋"
    leo         = "♌"
    virgo       = "♍"
    libra       = "♎"
    scorpio     = "♏"
    sagittarius = "♐"
    capricorn   = "♑"
    aquarius    = "♒"
    pisces      = "♓"

    @property
    def full(self) -> str:
        return self.name.capitalize()
    
    @property
    def symbol(self) -> str:
        return self.value

class Horo:
    '''Container class for individual horoscopes.'''
    def __init__(self, 
                 sign: ZodiacSign, 
                 date: str, 
                 text: str              = "",
                 source: Source         = Source.astrology_com, 
                 style: Style           = Style.daily
                 ) -> None:
        '''Container class for individual horoscopes. Served by Horoscope object with get_horoscope().
        :sign: Zodiac Sign, type: ZodiacSign
        :day: Day of horoscope, type: Day
        :text: Horoscope text, type: str
        :source: Source of horoscope. Default: Source.astrology_com
        :style: Style of horoscope, specific to Source.astrology_com. Unused if the source doesn't match. Default: AstrologyCom.Style.daily'''
        self.sign: ZodiacSign       = sign
        self.date: str              = date
        self.text: str              = text
        self.source: Source         = source
        
        if style not in source.styles:
            self.style = source.default_style
        else:
            self.style = style