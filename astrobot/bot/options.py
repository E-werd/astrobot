# External
from interactions import SlashCommandChoice
# Internal
from astrobot.core.datatypes import Day, Source, Style, ZodiacSign


class Options:
    @staticmethod
    def choice_zodiac() -> list:
        out: list[SlashCommandChoice]   = []
        full: str                       = ""

        for sign in ZodiacSign:
            full = sign.symbol + " " + sign.full
            out.append(SlashCommandChoice(name=full, value=sign.name))

        return out

    @staticmethod
    def choice_day() -> list:
        out: list[SlashCommandChoice]   = []
        full: str                       = ""

        for day in Day:
            full = day.symbol + " " + day.full
            out.append(SlashCommandChoice(name=full, value=day.name))

        return out

    @staticmethod
    def choice_style() -> list:
        out: list[SlashCommandChoice]   = []
        full: str                       = ""

        for style in Style:
            full = style.symbol + " " + style.full
            out.append(SlashCommandChoice(name=full, value=style.name))

        return out

    @staticmethod
    def choice_source() -> list:
        out: list[SlashCommandChoice]   = []

        for source in Source:
            out.append(SlashCommandChoice(name=source.full, value=source.name))

        return out
    
    @staticmethod
    async def ac_style(source: Source = Source.astrology_com) -> list:
        out: list[SlashCommandChoice]   = []
        full: str = ""

        for sty in source.styles:
            full = sty.symbol + " " + sty.full
            out.append(SlashCommandChoice(name=full, value=sty.name))

        return out
    
    @staticmethod
    async def ac_source(style: Style = Style.daily) -> list:
        out: list[SlashCommandChoice]   = []

        for source in Source:
            if (style in source.styles):
                out.append(SlashCommandChoice(name=source.full, value=source.name))

        return out