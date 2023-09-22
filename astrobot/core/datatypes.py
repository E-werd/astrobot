# External
from abc import ABC
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
            str: The name of the relative day capitalized.
        """
        return self.name.capitalize()

class Style(Enum):
    """Enum describing the possible horoscope styles.
    """
    daily       = "Daily Horoscope"
    daily_love  = "Daily Love Horoscope"

    @property
    def full(self) -> str:
        """Friendly name for the enum value.

        Returns:
            str: The value of the enum.
        """
        return self.value
    
    @property
    def symbol(self) -> str:
        """Emoji symbol for the horoscope style.

        Returns:
            str: A UTF8 emoji symbol.
        """
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
        """Friendly name for the enum value.

        Returns:
            str: The value of the enum.
        """
        return self.value
    
    @property
    def styles(self) -> list[Style]:
        """A list of styles that the source provides.

        Returns:
            list[Style]: The list of styles provided by the source.
        """
        style_list: dict[Source, list[Style]]   = {Source.horoscope_com:  [Style.daily, Style.daily_love],
                                                   Source.astrology_com:  [Style.daily, Style.daily_love],
                                                   Source.astrostyle:     [Style.daily]}
        return style_list[self]
    
    @property
    def default_style(self) -> Style:
        """The default style for the source. Used when the style requested doesn't exist in the styles list.

        Returns:
            Style: A style that is the default for the source.
        """
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
        """Capitalized version of the name, for presentation.

        Returns:
            str: The name of the zodiac sign capitalized.
        """
        return self.name.capitalize()
    
    @property
    def symbol(self) -> str:
        """Emoji symbol for the zodiac sign. A friendly name for the enum value.

        Returns:
            str: A UTF8 emoji symbol.
        """
        return self.value

class Horo:
    """Container class for individual horoscopes.
    """
    def __init__(self, 
                 sign: ZodiacSign, 
                 date: str, 
                 text: str              = "",
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
        self.sign: ZodiacSign       = sign
        self.date: str              = date
        self.text: str              = text
        self.source: Source         = source
        
        if style not in source.styles:
            self.style = source.default_style
        else:
            self.style = style

class HoroSource(ABC):
    """Abstract class declaring a generic Horoscope Source.
    """
    def __init__(self, sign: ZodiacSign, day: Day, style: Style) -> None:
        """Abstract class declaring a generic Horoscope Source.
        """
        self.date = ""
        self.text = ""

    @staticmethod
    def create_source_structure() -> dict: # type: ignore
        """Creates empty data structure for source data. Should be called from __create_data().

        Returns:
            dict: Dict containing empty data structure.
        """
        pass