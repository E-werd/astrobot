#!/usr/bin/env python3
import logging, sys
from interactions import Client, listen, SlashCommandChoice, OptionType, slash_command, slash_option, SlashContext
from horoscope import getHoro, preloadData
from dotenv import load_dotenv
from os import getenv

# Vars
load_dotenv()
TOKEN = getenv("TOKEN", default="none")
FILE = getenv("DATAFILE", default="data.json")
LOGLEVEL = getenv("LOGLEVEL", default="error")

if TOKEN == "none":
    logging.critical("Missing token! Set TOKEN in .env, see .env.example")
    sys.exit("Exiting.")

style_string = {"daily": "Daily", "daily-love": "Daily Love"}

# Logging
logopt = { "debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING , "error": logging.ERROR, "critical": logging.CRITICAL }
logging.basicConfig(level=logopt.get(LOGLEVEL, logging.INFO))

# Bot stuff
bot = Client(token=TOKEN)

@slash_command(
        name="horoscope",
        description="Show horoscope for specified sign"
        )
@slash_option(
        name="sign",
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
async def horoscope(ctx: SlashContext, sign: str, day: str = "today", style: str = "daily"):
    h = getHoro(sign, FILE)
    await ctx.send("__" + style_string[style] + " Horoscope for **" + h["name"] + "**" + " for " + "*" + h[style][day]["date"] + "*__: " +  "\n" + h[style][day]["horoscope"])

@listen()
async def on_ready(self):
    logging.info("Logged on as: " + bot.app.name)

# Startup
logging.info("Preloading data...")
preloadData(FILE)
logging.info("Done.")

logging.info("Starting bot...")
bot.start()