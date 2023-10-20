# External
import logging
from datetime import datetime
from dateutil.parser import parse
from interactions.ext.paginators import Paginator
from interactions import (OptionType, slash_command, slash_option, SlashContext, Embed)
# Internal
from astrobot.bot.options import Options
from astrobot.core.common import Misc
from astrobot.modules.chart import ChartUser
from astrobot.core.astrology import ZodiacSign
from astrobot.modules.horoscope import Horo, HoroItem
from astrobot.modules.common import Day, Source, Style


class Commands:
    def __init__(self, bing_api: str) -> None:
        """Commands for the bot.

        Args:
        bing_api (str): The Bing API key.
        data (Data): The Data object holding data.
        """
        self.bing_api: str      = bing_api

    # Commands
    @slash_command(
            name="horoscope",
            description="Show horoscope for specified sign"
        )
    @slash_option(
            name="sign",
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
    async def horoscope(self, ctx: SlashContext, sign: str, day: str = "today", style: str = "daily", source: str = "astrology_com"):
        # Prepare data for horoscope fetch
        _sign: ZodiacSign       = ZodiacSign[sign]
        _day: Day               = Day[day]
        _style: Style           = Style[style]
        _source: Source         = Source[source]

        # Log request
        logging.info(f"Received 'horoscope' request from '{ctx.user.username}' [{ctx.author_id}] with parameters: sign: {_sign.name}, day: {_day.name}, style: {_style.name}, source: {_source.name}")

        # Gather data
        item: HoroItem          = HoroItem(day=_day, source=_source, style=_style, sign=_sign)
        hor: Horo               = await item.fetch()

        # Format data into a list
        day_of_week: str        = Misc.get_day_of_week_from_string(string=hor.date).capitalize() + ","
        header: list[str]       = ["### ", 
                                   hor.sign.symbol, hor.sign.full, 
                                   hor.style.symbol, hor.style.full, 
                                   "for", _day.symbol, 
                                   day_of_week, hor.date,
                                   "from", hor.source.full]
        body: str               = hor.text

        # Put data into single string, send
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
        charts: dict[str, str]  = user.get_charts_as_str()

        # Format data into a list of embeds
        embed: list[Embed] = []
        for name, chart in charts.items():
            content: list[str]  = ["```"]
            content.append(chart)
            content.append("```")
            embed.append( Embed(title=name, description="\n".join(content)) )

        # Create paginator and send
        paginator: Paginator    = Paginator.create_from_embeds(ctx.client, *embed)
        await paginator.send(ctx=ctx)