# External
from abc import ABC
from enum import Enum
# Internal
from astrobot.core.astrology import ZodiacSign


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