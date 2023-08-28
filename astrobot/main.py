# External
import logging, sys
from dotenv import load_dotenv
from os import getenv
# Internal
from astrobot.core.data import Data
from astrobot.core.bot import Bot


class Main:
    '''Main class to run AstroBot'''
    def __init__(self) -> None:
        '''Main class to run AstroBot'''
        self.TOKEN: str     = ""
        self.FILE: str      = ""
        self.LOGLEVEL: str  = ""
        
        # Load environment vars
        if not self.__load_env():
            logging.critical("Missing token! Set TOKEN in .env, see .env.example")
            sys.exit("Exiting.")

        # Setup logging
        self.__set_logging()

        # Setup data and bot
        self.data: Data     = Data(file=self.FILE, source=Data.Source.json)
        self.bot: Bot       = Bot(token=self.TOKEN, data=self.data)

    def __load_env(self) -> bool:
        '''Loads from .env using dotenv'''
        load_dotenv()
        self.TOKEN: str     = getenv("TOKEN", default="none")
        self.FILE: str      = getenv("DATAFILE", default="data.json")
        self.LOGLEVEL: str  = getenv("LOGLEVEL", default="error")

        if (self.TOKEN == "none"): return False
        else: return True

    def __set_logging(self) -> None:
        '''Sets logging options'''
        logopt: dict[str, int]  = { "debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING , "error": logging.ERROR, "critical": logging.CRITICAL }
        format: str             = "[%(asctime)s.%(msecs)03d][%(levelname)s][%(filename)s:%(lineno)s] %(message)s"
        datefmt: str            = "%Y-%m-%d %H:%M:%S"
        level: int              = logopt.get(self.LOGLEVEL, logging.INFO)
        logging.basicConfig(format=format, datefmt=datefmt, level=level)

    def start(self) -> None:
        '''Starts bot'''
        self.bot.start()