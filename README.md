# AstroBot

This is a simple discord bot to get daily horoscopes from a reliable source.  This was born out of a dislike for the Zodiac Bot in a server I'm in which seems basically pulls horoscopes from a list which eventually results in repeats, which also means that the horoscope isn't written with the current state of the stars in mind--basically a fortune cookie.

Requirements:
- Python 3.10+
- beautifulsoup4>=4.10.0
- discord_py_interactions>=5.7.0
- python-dotenv>=1.0.0
- Requests>=2.31.0

Based on [interactions.py](https://interactions-py.github.io/interactions.py/).

Adds the ```/horoscope``` command.  The horoscope data is scraped from astrology.com.

Requires a token in ```.env```, see ```.env.example```.

Data is kept locally in a file to avoid scraping for every request.  Data is checked for updates every 30 minutes according to a registered task in ```bot.py```, updated data is written back to the file.

Run with ```python3 -m astrobot```