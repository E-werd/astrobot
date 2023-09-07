# External
import logging
from interactions import (OptionType, slash_command, slash_option, SlashContext)
from dateutil.parser import parse
from datetime import datetime
# Internal
from astrobot.core.data import Data
from astrobot.core.datatypes import Day, Source, Style, Horo, Zodiac
from astrobot.bot.options import Options
from astrobot.modules.horoscope import Horoscope
from astrobot.modules.chart import ChartUser


class Commands:
    def __init__(self, bing_api: str, data: Data) -> None:
        # Create Data and Horoscope objects, local dict
        self.file: Data         = data
        self.data: dict         = self.file.data # Only do this the first time, otherwise use self.file.load_data()
        self.scope: Horoscope   = Horoscope(data=self.data)
        self.bing_api: str      = bing_api

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
        Day.update()
        _sign: Zodiac.Type      = Zodiac.types[zodiac]
        _day: Day.Type          = Day.types[day]
        _style: Style.Type      = Style.types[style]
        _source: Source.Type    = Source.types[source]
        logging.info(f"Received 'horoscope' request from '{ctx.user.username}' [{ctx.author_id}] with parameters: sign: {_sign.name}, day: {_day.name}, style: {_style.name}, source: {_source.name}")

        self.data               = self.file.load_data()
        hor: Horo               = self.scope.get_horoscope(zodiac=_sign, day=_day, source=_source, style=_style, data=self.data)
        header: list[str]       = ["### ", 
                                   hor.zodiac.symbol, hor.zodiac.full, 
                                   hor.style.symbol, hor.style.full, 
                                   "for", _day.symbol, hor.date,
                                   "from", hor.source.full]
        body: str               = hor.text
        msg: str                = " ".join(header) + "\n" + body
        
        await ctx.send(msg)

    @slash_command(
        name="chart",
        description="Get natal chart"
    )
    @slash_option(
            name="location",
            description="Birth city",
            opt_type=OptionType.STRING,
            required=True
            )
    @slash_option(
            name="birthday",
            description="Birth date, with leading zero (e.g. 07/04/1776) [MM/DD/YYYY]",
            opt_type=OptionType.STRING,
            required=True
            )
    @slash_option(
            name="birthtime",
            description="Birth time, 24-hour format (e.g. 14:30) [HH:MM] -- Optional, will assume 00:00",
            opt_type=OptionType.STRING,
            required=False
            )
    async def chart(self, ctx: SlashContext, location: str, birthday: str, birthtime: str = "00:00"):
        # Log request
        logging.info(f"Received 'chart' request from '{ctx.user.username}' [{ctx.author_id}] with parameters: location: {location}, birthday: {birthday}, birthtime: {birthtime}")
        
        # Combine birthday and birthtime, parse and try to get good data.
        dt_str: str             = birthtime + " " + birthday
        date: datetime          = parse(timestr=dt_str, fuzzy=True)
        good_date: str          = date.strftime("%m/%d/%Y")
        good_time: str          = date.strftime("%H:%M")

        # Gather data
        user: ChartUser         = ChartUser(
                                      bing_api=self.bing_api,
                                      name=ctx.user.display_name,
                                      location=location,
                                      birthday=good_date,
                                      time=good_time
                                      )
        chart: list[str]        = user.get_charts_as_str()

        # Format data into a list
        send: list[str]         = [f"Natal planet and house tables requested by {ctx.user.mention}:", "```"]
        for s in chart:
            send.append(s)
        send.append("```")

        # Put data into single string, send
        msg: str = "\n".join(send)
        await ctx.send(msg)