#!/usr/bin/env python3
# External
import logging, sys
from dotenv import load_dotenv
from os import getenv
# Internal
from bot import Bot
from data import Data
from horoscope import Horoscope

class Main:
    '''Main class to run AstroBot'''
    def __init__(self) -> None:
        '''Main class to run AstroBot'''
        self.TOKEN: str = ""
        self.FILE: str = ""
        self.LOGLEVEL: str = ""
        
        # Load environment vars
        if not self.__load_env():
            logging.critical("Missing token! Set TOKEN in .env, see .env.example")
            sys.exit("Exiting.")

        # Setup logging
        self.__set_logging()

        # Setup data and bot
        self.data: Data = Data(file=self.FILE, source=Data.Source.json)
        self.horoscope: Horoscope = Horoscope(file=self.data)
        self.bot: Bot = Bot(token=self.TOKEN, horoscope=self.horoscope)

    def __load_env(self) -> bool:
        '''Loads from .env using dotenv'''
        load_dotenv()
        self.TOKEN = getenv("TOKEN", default="none")
        self.FILE = getenv("DATAFILE", default="data.json")
        self.LOGLEVEL = getenv("LOGLEVEL", default="error")

        if (self.TOKEN == "none"): return False
        else: return True

    def __set_logging(self) -> None:
        '''Sets logging options'''
        logopt: dict = { "debug": logging.DEBUG, "info": logging.INFO, "warning": logging.WARNING , "error": logging.ERROR, "critical": logging.CRITICAL }
        format: str = "[%(asctime)s.%(msecs)03d][%(levelname)s][%(filename)s:%(lineno)s] %(message)s"
        datefmt: str = "%Y-%m-%d %H:%M:%S"
        level = logopt.get(self.LOGLEVEL, logging.INFO)
        logging.basicConfig(format=format, datefmt=datefmt, level=level)

    def start(self) -> None:
        '''Starts bot'''
        self.bot.start()

# Starting point
if __name__ == "__main__":
    main: Main = Main()
    main.start()