# External
from enum import Enum


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