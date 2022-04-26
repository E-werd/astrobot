**AstoBot**

This is a simple discord bot that adds the '''/horoscope''' command.  The horoscope data is pulled from an unofficial repository that scrapes astrology.com.  The API is located here: http://ohmanda.com/api/horoscope/

Requires a token in '''.env''', see '''.env.example'''.  Set a cronjob to run '''update.py''':

'''
0 6 * * * ~/astrobot/update.py
'''

This runs at 6am daily.  I believe 6am ET is long enough to allow the API to update itself, but you might have to play with it.


Uses [interactions.py](https://discord-interactions.readthedocs.io/en/latest/index.html).
