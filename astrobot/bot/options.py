# External
from interactions import SlashCommandChoice
# Internal
from astrobot.core.datatypes import Day, Source, Style, Zodiac


class Options:
    @staticmethod
    def choice_zodiac() -> list:
        out: list[SlashCommandChoice]   = []
        full: str                       = ""

        for name, obj in Zodiac.types.items():
            full = obj.symbol + " " + obj.full
            out.append(SlashCommandChoice(name=full, value=name))

        return out

    @staticmethod
    def choice_day() -> list:
        out: list[SlashCommandChoice]   = []
        full: str                       = ""

        for name, obj in Day.types.items():
            full = obj.symbol + " " + obj.full
            out.append(SlashCommandChoice(name=full, value=name))

        return out

    @staticmethod
    def choice_style() -> list:
        out: list[SlashCommandChoice]   = []
        full: str                       = ""

        for name, obj in Style.types.items():
            full = obj.symbol + " " + obj.full
            out.append(SlashCommandChoice(name=full, value=name))

        return out

    @staticmethod
    def choice_source() -> list:
        out: list[SlashCommandChoice]   = []

        for name, obj in Source.types.items():
            out.append(SlashCommandChoice(name=obj.full, value=name))

        return out
    
    @staticmethod
    async def ac_style(source: Source.Type = Source.astrology_com) -> list:
        out: list[SlashCommandChoice]   = []
        full: str = ""

        for sty in source.styles:
            full = sty.symbol + " " + sty.full
            out.append(SlashCommandChoice(name=full, value=sty.name))

        return out
    
    @staticmethod
    async def ac_source(style: Style.Type = Style.daily) -> list:
        out: list[SlashCommandChoice]   = []

        for name, obj in Source.types.items():
            if (style in obj.styles):
                out.append(SlashCommandChoice(name=obj.full, value=name))

        return out