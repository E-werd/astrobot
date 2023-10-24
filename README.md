# AstroBot

This is a simple discord bot to get daily horoscopes from reliable sources.  This project was born out of a dislike for a Zodiac Bot in a server I'm in which seems to pull horoscopes from a list which eventually results in repeats, which also means that the horoscope isn't written with the current state of the stars in mind--basically a fortune cookie.

Requires Python 3.10+. See [requirements.txt](requirements.txt) for more information about dependencies.

Bot code based on [interactions.py](https://interactions-py.github.io/interactions.py/).

Adds the ```/horoscope``` and ```/chart``` commands.  The horoscope data is scraped from three sources: Astrology.com, Horoscope.com, and AstroStyle.com. HTTP responses are cached locally to avoid unnececssary hits to the sources.

Requires tokens for Discord and Bing in ```.env```, see [.env.example](.env.example).

Run with ```python3 -m astrobot``` or ```run.sh```.