#!/usr/bin/env python3
from horoscope import updateHoro
from dotenv import load_dotenv
from os import getenv

load_dotenv()
FILE = getenv('DATAFILE')

print("Updating data...")
updateHoro(FILE)
print("Done.")