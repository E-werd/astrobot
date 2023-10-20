# External
from interactions import SlashCommandChoice
# Internal
from astrobot.core.astrology import ZodiacSign
from astrobot.modules.common import Day, Source, Style


class Options:
    @staticmethod
    def choice_zodiac() -> list:
        """Generate choices for zodiac signs.

        Returns:
            list: A list of slash command choices.
        """
        out: list[SlashCommandChoice]   = []
        full: str                       = ""

        for sign in ZodiacSign:
            full = sign.symbol + " " + sign.full
            out.append(SlashCommandChoice(name=full, value=sign.name))

        return out

    @staticmethod
    def choice_day() -> list:
        """Generate choices for available days.

        Returns:
            list: A list of slash command choices.
        """
        out: list[SlashCommandChoice]   = []
        full: str                       = ""

        for day in Day:
            full = day.symbol + " " + day.full
            out.append(SlashCommandChoice(name=full, value=day.name))

        return out

    @staticmethod
    def choice_style() -> list:
        """Generate choices for horoscope styles.

        Returns:
            list: A list of slash command choices.
        """
        out: list[SlashCommandChoice]   = []
        full: str                       = ""

        for style in Style:
            full = style.symbol + " " + style.full
            out.append(SlashCommandChoice(name=full, value=style.name))

        return out

    @staticmethod
    def choice_source() -> list:
        """Generate choices for horoscope sources.

        Returns:
            list: A list of slash command choices.
        """
        out: list[SlashCommandChoice]   = []

        for source in Source:
            out.append(SlashCommandChoice(name=source.full, value=source.name))

        return out