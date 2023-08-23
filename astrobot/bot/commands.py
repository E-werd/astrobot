# External
import logging
from interactions import (OptionType, slash_command, slash_option, SlashContext)
# Internal
from astrobot.core.data import Data
from astrobot.core.datatypes import Day, Source, Style, Horo, Zodiac
from astrobot.bot.options import Options
from astrobot.modules.horoscope import Horoscope


class Commands:
    def __init__(self, data: Data) -> None:
        # Create Data and Horoscope objects, local dict
        self.file: Data = data
        self.data: dict = self.file.data # Only do this the first time, otherwise use self.file.load_data()
        self.scope: Horoscope = Horoscope(data=self.data)

    @slash_command(
            name="horoscope",
            description="Show horoscope for specified sign"
        )
    @slash_option(
            name="zodiac",
            description="zodiac sign",
            opt_type=OptionType.STRING,
            required=True,
            choices=Options.choice_zodiac()
            )
    @slash_option(
            name="day",
            description="day",
            opt_type=OptionType.STRING,
            required=False,
            choices=Options.choice_day()
            )
    @slash_option(
            name="style",
            description="horoscope style",
            opt_type=OptionType.STRING,
            required=False,
            choices=Options.choice_style()
            )
    @slash_option(
            name="source",
            description="horoscope source",
            opt_type=OptionType.STRING,
            required=False,
            choices=Options.choice_source()
            )
    async def horoscope(self, ctx: SlashContext, zodiac: str, day: str = "today", style: str = "daily", source: str = "astrology_com"):
        _sign: Zodiac.Type = Zodiac.types[zodiac]
        _day: Day.Type = Day.types[day]
        _style: Style.Type = Style.types[style]
        _source: Source.Type = Source.types[source]
        logging.info(f"Received 'horoscope' request from '{ctx.user.username}' [{ctx.author_id}] with parameters: sign: {_sign.name}, day: {_day.name}, style: {_style.name}, source: {_source.name}")

        self.data = self.file.load_data()
        hor: Horo = self.scope.get_horoscope(zodiac=_sign, day=_day, source=_source, style=_style, data=self.data)
        horday: Day.Type = self.scope.get_day(hor.date)
        header: list[str] = ["### ", 
                             hor.zodiac.symbol, hor.zodiac.full, 
                             hor.style.symbol, hor.style.full, 
                             "for", horday.symbol, hor.date,
                             "from", hor.source.full]
        body: str = hor.text
        msg: str = " ".join(header) + "\n" + body
        
        await ctx.send(msg)