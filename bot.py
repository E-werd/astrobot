# External
import logging
from interactions import (AutoShardedClient, listen, SlashCommandChoice, 
                          OptionType, slash_command, slash_option, 
                          SlashContext, Task, IntervalTrigger)
# Internal
from datatypes import Day, Source, Style, Horo, Zodiac
from data import Data
from horoscope import Horoscope

class Bot(AutoShardedClient):
    '''Wrapped class for interactions.py client'''
    def __init__(self, token: str, file: Data):
        '''Wrapped class for interactions.py client
        :token: Token for authentication
        :horoscope: Horoscope object'''
        super(Bot, self).__init__(token=token)
        self.scope: Horoscope = Horoscope(file=file)

    # Listeners
    @listen()
    async def on_startup(self):
        logging.info("Starting update check task.")
        self.check_updates.start()

    @listen()
    async def on_ready(self):
        logging.info(f"Logged on as: {self.app.name}")
        
    # Tasks
    @Task.create(IntervalTrigger(minutes=30))
    async def check_updates(self):
        self.scope.check_updates()

    # Commands
    @slash_command(
            name="horoscope",
            description="Show horoscope for specified sign"
        )
    @slash_option(
            name="zodiac",
            description="zodiac sign",
            opt_type=OptionType.STRING,
            required=True,
            choices=[
                SlashCommandChoice(name="♈ Aries", value="aries"),
                SlashCommandChoice(name="♉ Taurus", value="taurus"),
                SlashCommandChoice(name="♊ Gemini", value="gemini"),
                SlashCommandChoice(name="♋ Cancer", value="cancer"),
                SlashCommandChoice(name="♌ Leo", value="leo"),
                SlashCommandChoice(name="♍ Virgo", value="virgo"),
                SlashCommandChoice(name="♎ Libra", value="libra"),
                SlashCommandChoice(name="♏ Scorpio", value="scorpio"),
                SlashCommandChoice(name="♐ Sagittarius", value="sagittarius"),
                SlashCommandChoice(name="♑ Capricorn", value="capricorn"),
                SlashCommandChoice(name="♒ Aquarius", value="aquarius"),
                SlashCommandChoice(name="♓ Pisces", value="pisces"),
            ]
            )
    @slash_option(
            name="day",
            description="day",
            opt_type=OptionType.STRING,
            required=False,
            choices=[
                SlashCommandChoice(name="▶️ Today", value="today"),
                SlashCommandChoice(name="⏭️ Tomorrow", value="tomorrow"),
                SlashCommandChoice(name="⏮️ Yesterday", value="yesterday"),
            ]
            )
    @slash_option(
            name="style",
            description="horoscope style",
            opt_type=OptionType.STRING,
            required=False,
            choices=[
                SlashCommandChoice(name="🌅 Daily", value="daily"),
                SlashCommandChoice(name="💗 Daily Love", value="daily-love"),
            ]
            )
    async def horoscope(self, ctx: SlashContext, zodiac: str, day: str = "today", style: str = "daily", source: str = "astrology_com"):
        _sign: Zodiac.Type = Zodiac.types[zodiac]
        _day: Day.Type = Day.types[day]
        _style: Style.Type = Style.types[style]
        _source: Source.Type = Source.types[source]
        logging.info(f"Received 'horoscope' request from '{ctx.user.username}' [{ctx.author_id}] with parameters: sign: {_sign.name}, day: {_day.name}, style: {_style.name}, source: {_source.name}")

        hor: Horo = self.scope.get_horoscope(zodiac=_sign, day=_day, source=_source, style=_style)
        header: list[str] = ["### ", 
                             hor.zodiac.symbol, hor.zodiac.full, 
                             hor.style.symbol, hor.style.full, 
                             "for", hor.day.symbol, hor.day.long]
        body: str = hor.text
        msg: str = " ".join(header) + "\n" + body

        await ctx.send(msg)