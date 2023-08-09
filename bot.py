# External
import logging
from interactions import (AutoShardedClient, listen, SlashCommandChoice, 
                          OptionType, slash_command, slash_option, 
                          SlashContext, AutocompleteContext, Task, 
                          IntervalTrigger)
# Internal
from datatypes import Day, Source, Style, Horo, Zodiac
from data import Data
from horoscope import Horoscope

class Bot(AutoShardedClient):
    '''Wrapped class for interactions.py client'''
    def __init__(self, token: str, data: Data):
        '''Wrapped class for interactions.py client
        :token: Token for authentication
        :horoscope: Horoscope object'''
        super(Bot, self).__init__(token=token)

        # Create Data and Horoscope objects, local dict
        self.file: Data = data
        self.data: dict = self.file.data # Only do this the first time, otherwise use self.file.load_data()
        self.scope: Horoscope = Horoscope(data=self.data)

        # Instantiation of Horoscope updates data we sent, return it to local dict and file; write.
        self.data = self.scope.data
        self.file.data = self.data
        self.file.write_data()

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
        # Read data from file, check for updates, sync and write back.
        self.data = self.file.load_data()
        self.data = self.scope.check_updates(data=self.data)
        self.file.data = self.data
        self.file.write_data()

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
    @slash_option(
            name="source",
            description="horoscope source",
            opt_type=OptionType.STRING,
            required=False,
            choices=[
                SlashCommandChoice(name="Astrology.com", value="astrology_com"),
                SlashCommandChoice(name="AstroStyle.com", value="astrostyle"),
            ]
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
                             "from", _source.full]
        body: str = hor.text
        msg: str = " ".join(header) + "\n" + body

        await ctx.send(msg)