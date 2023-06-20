#!/usr/bin/env python3
import logging, sys
from interactions import Client, listen, SlashCommandChoice, OptionType, slash_command, slash_option, SlashContext, Member
from horoscope import getHoro, loadData
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

# Logging
logopt = { "debug" : logging.DEBUG, "info" : logging.INFO, "error" : logging.ERROR }
logging.basicConfig(level=logopt.get(LOGLEVEL, logging.ERROR))

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
        name="when",
        description="when",
        opt_type=OptionType.STRING,
        required=False,
        choices=[
            SlashCommandChoice(name="Today", value="today"),
            SlashCommandChoice(name="Tomorrow", value="tomorrow"),
            SlashCommandChoice(name="Yesterday", value="yesterday"),
        ]
        )
async def horoscope(ctx: SlashContext, sign: str, when: str = "today"):
    h = getHoro(sign, FILE)
    await ctx.send("__**" + h["name"] + "**" + " for " + "*" + h[when]["date"] + "*__: " +  "\n" + h[when]["horoscope"])

@listen()
async def on_ready(self):
    print("Logged on as: " + bot.app.name)

# Startup
print("Loading data...")
loadData(FILE)
print("Done.")

print("Starting bot...")
bot.start()