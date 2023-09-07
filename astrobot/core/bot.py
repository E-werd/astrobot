# External
import logging
from interactions import (AutoShardedClient, listen, Task, IntervalTrigger)
# Internal
from astrobot.core.data import Data
from astrobot.modules.horoscope import Horoscope
from astrobot.bot.commands import Commands


class Bot(AutoShardedClient, Commands):
    '''Wrapped class for interactions.py client'''
    def __init__(self, token: str, bing_api: str, data: Data):
        '''Wrapped class for interactions.py client
        :token: Token for authentication
        :horoscope: Horoscope object'''

        # Create Data and Horoscope objects, local dict
        self.file: Data         = data
        self.data: dict         = self.file.data # Only do this the first time, otherwise use self.file.load_data()
        self.scope: Horoscope   = Horoscope(data=self.data)

        # Call parent class initialization
        AutoShardedClient.__init__(self, token=token)
        Commands.__init__(self, bing_api=bing_api, data=self.file)

        # Instantiation of Horoscope updates data we sent, return it to local dict and file; write.
        self.data               = self.scope.data
        self.file.data          = self.data
        self.file.write_data()

    # Listeners
    @listen()
    async def on_startup(self):
        logging.info("Starting update check task.")
        self.check_updates.start()

    @listen()
    async def on_ready(self):
        logging.info(f"Logged on as: {self.app.name}")
        
    # Tasks
    @Task.create(IntervalTrigger(minutes=30))
    async def check_updates(self):
        # Read data from file, check for updates, sync and write back.
        self.data       = self.file.load_data()
        self.data       = self.scope.check_updates(data=self.data)
        self.file.data  = self.data
        self.file.write_data()