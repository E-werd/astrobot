#!/usr/bin/env python3
import logging, interactions, sys
from horoscope import getHoro, updateHoro, checkData
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
bot = interactions.Client(token=TOKEN)

@bot.command(
    name="horoscope",
    description="Show horoscope for specified sign",
    options =[
        interactions.Option(
            name="sign",
            description="zodiac sign",
            type=interactions.OptionType.STRING,
            required=True,
            choices=[
                interactions.Choice(name="♈ Aries", value="aries"),
                interactions.Choice(name="♉ Taurus", value="taurus"),
                interactions.Choice(name="♊ Gemini", value="gemini"),
                interactions.Choice(name="♋ Cancer", value="cancer"),
                interactions.Choice(name="♌ Leo", value="leo"),
                interactions.Choice(name="♍ Virgo", value="virgo"),
                interactions.Choice(name="♎ Libra", value="libra"),
                interactions.Choice(name="♏ Scorpio", value="scorpio"),
                interactions.Choice(name="♐ Sagittarius", value="sagittarius"),
                interactions.Choice(name="♑ Capricorn", value="capricorn"),
                interactions.Choice(name="♒ Aquarius", value="aquarius"),
                interactions.Choice(name="♓ Pisces", value="pisces"),
            ]
        ),
    ],
)
@interactions.autodefer()
async def horoscope(ctx: interactions.CommandContext, sign: str):
    h = getHoro(sign, FILE)
    await ctx.send(sign.capitalize() + " for " + h["date"] + ": \n\n" + h["horoscope"])

@bot.event
async def on_ready():
    print("Logged on as:" + bot.me.name)

# Startup
print("Checking local data...")
if not checkData(FILE):
    updateHoro(FILE)
print("Done.")

print("Starting bot...")
bot.start()