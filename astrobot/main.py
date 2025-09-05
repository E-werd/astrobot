# External
import logging, sys
from os import getenv
from dotenv import load_dotenv
# Internal
from astrobot.core.bot import Bot


class Main:
    """Main class to run AstroBot.
    """
    def __init__(self) -> None:
        """Main class to run AstroBot.
        """
        self.TOKEN: str     = ""
        self.GEO_API: str  = ""
        self.LOGLEVEL: str  = ""
        
        # Load environment vars
        load, msg = self.__load_env()
        if not load:
            logging.critical(msg)
            sys.exit("Exiting.")

        # Setup logging
        self.__set_logging()

        # Setup data and bot
        self.bot: Bot       = Bot(token=self.TOKEN, geo_api=self.GEO_API)

    def __load_env(self) -> tuple[bool, str]:
        """Loads from .env using dotenv.

        Returns:
            tuple[bool, str]: A tuple containing a bool and string. If bad, returns False and a message. Good is True and blank.
        """
        load_dotenv()
        self.TOKEN: str     = getenv("TOKEN", default="none")
        self.GEO_API: str  = getenv("GEO_API", default="none")
        self.LOGLEVEL: str  = getenv("LOGLEVEL", default="error")

        if (self.TOKEN == "none"): 
            return False, "Missing Discord bot token! Set TOKEN in .env, see .env.example"
        
        if (self.GEO_API == "none"):
            return False, "Missing Geocoder API key! Set GEO_API in .env, see .env.example"
        
        return True, ""

    def __set_logging(self) -> None:
        """Sets logging options and format.
        """
        logopt: dict[str, int]  = { "debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING , "error": logging.ERROR, "critical": logging.CRITICAL }
        format: str             = "[%(asctime)s.%(msecs)03d][%(levelname)s][%(filename)s:%(lineno)s] %(message)s"
        datefmt: str            = "%Y-%m-%d %H:%M:%S"
        level: int              = logopt.get(self.LOGLEVEL, logging.INFO)
        logging.basicConfig(format=format, datefmt=datefmt, level=level)

    def start(self) -> None:
        """Starts the bot.
        """
        self.bot.start()