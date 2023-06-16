# AstroBot

This is a simple discord bot to get daily horoscopes from a reliable source.  This was born out of a dislike for the Zodiac Bot in a server I'm in which seems basically pulls horoscopes from a list which eventually results in repeats, which also means that the horoscope isn't written with the current state of the stars in mind--basically a fortune cookie.

Based on [interactions.py](https://interactions-py.github.io/interactions.py/).

Adds the ```/horoscope``` command.  The horoscope data is scraped from astrology.com.

Requires a token in ```.env```, see ```.env.example```.

Data is kept locally in a file to avoid scraping for every request.  This file needs to be updated once per day.  Set a cron job to run ```update.py```:

```
0 6 * * * cd ~/astrobot && ./update.py
```

This runs at 6am daily.  I believe 6am ET is long enough to allow the site to update itself, but you might have to play with it.  This time has worked for me so far.

* TODO: Find a way to update without relying on a cron job.  Check the date in the file and choosing when to update the following day.  Something like "if current date if after data date and at least 6am, update".  Once this is done, store data in memory and update it when the file is updated to reduce hits on file system.