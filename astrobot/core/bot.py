# External
import logging
from interactions import (AutoShardedClient, listen)
from interactions.api.events import (Startup, Ready, Login, Disconnect)
# Internal
from astrobot.core.data import Data
from astrobot.bot.commands import Commands


class Bot(AutoShardedClient, Commands):
    """Wrapped class for interactions.py client.
    """
    def __init__(self, token: str, bing_api: str, data: Data):
        """Wrapped class for interactions.py client.

        Args:
            token (str): Token for bot authentication.
            bing_api (str): Pass-through for Bing API key, used for charts.
            data (Data): Data object for access to stored horoscope data.
        """
        # Call parent class initialization
        AutoShardedClient.__init__(self, token=token)
        Commands.__init__(self, bing_api=bing_api, data=data)

    # Event Listeners
    @listen(Startup)
    async def event_startup(self):
        logging.info("STARTUP: Starting update check task.")
        self.check_updates.start()

    @listen(Login)
    async def event_login(self):
        logging.info(f"LOGIN: Logged on as: {self.app.name}")

    @listen(Ready)
    async def event_ready(self):
        logging.info("READY: Bot is ready.")

    @listen(Disconnect)
    async def event_disconnect(self):
        logging.info("DISCONNECT: Stopping bot.")