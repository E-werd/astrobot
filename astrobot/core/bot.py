# External
import logging
from interactions import (AutoShardedClient, listen)
from interactions.api.events import (Startup, Ready, Login, Disconnect)
# Internal
from astrobot.bot.commands import Commands
from astrobot.modules.horoscope import HoroItem


class Bot(AutoShardedClient, Commands):
    """Wrapped class for interactions.py client.
    """
    def __init__(self, token: str, geo_api: str):
        """Wrapped class for interactions.py client.

        Args:
            token (str): Token for bot authentication.
            geo_api (str): Pass-through for Geocoder API key, used for charts.
        """
        # Call parent class initialization
        AutoShardedClient.__init__(self, token=token)
        Commands.__init__(self, geo_api=geo_api)

    # Event Listeners
    @listen(Startup)
    async def event_startup(self):
        await HoroItem.precache()

    @listen(Login)
    async def event_login(self):
        logging.info(f"LOGIN: Logged on as: {self.app.name}")

    @listen(Ready)
    async def event_ready(self):
        logging.info("READY: Bot is ready.")

    @listen(Disconnect)
    async def event_disconnect(self):
        logging.info("DISCONNECT: Stopping bot.")