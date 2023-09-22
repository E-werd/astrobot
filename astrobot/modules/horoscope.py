# External
import logging, random
from datetime import datetime
# Internal
from astrobot.core.common import Misc
from astrobot.core.astrology import ZodiacSign
from astrobot.modules.sources.common import Day, Source, Style, HoroSource
# Sources
from astrobot.modules.sources.astrologycom import AstrologyCom
from astrobot.modules.sources.astrostyle import Astrostyle
from astrobot.modules.sources.horoscopecom import HoroscopeCom


class Horo:
    """Container class for individual horoscopes.
    """
    def __init__(self, 
                 sign: ZodiacSign, 
                 date: str, 
                 text: str              = "",
                 source: Source         = Source.astrology_com, 
                 style: Style           = Style.daily
                 ) -> None:
        """Container class for individual horoscopes. Served by Horoscope object with get_horoscope().

        Args:
            sign (ZodiacSign): Zodiac sign.
            date (str): Formatted date string, use a function from Misc to generate.
            text (str, optional): Horoscope text. Defaults to "".
            source (Source, optional): Source of horoscope. Defaults to Source.astrology_com.
            style (Style, optional): Style of horoscope. Defaults to Style.daily.
        """
        self.sign: ZodiacSign       = sign
        self.date: str              = date
        self.text: str              = text
        self.source: Source         = source
        
        if style not in source.styles:
            self.style = source.default_style
        else:
            self.style = style

class Horoscope:
    """Work with horoscopes, wraps all sources.
    """
    def __init__(self, data: dict) -> None:
        """Work with horoscopes, wraps all sources.

        Args:
            data (dict): Dictionary with or without data.
        """
        # Declare all possible types for use later
        self.__source: dict[Source, HoroSource]     = {Source.astrology_com:    AstrologyCom, # type: ignore
                                                       Source.astrostyle:       Astrostyle,
                                                       Source.horoscope_com:    HoroscopeCom}
        self.data: dict                             = self.__prep_data(data=data)

    def __create_structure(self) -> dict:
        """Creates empty data structure.

        Returns:
            dict: A formatted dictionary, a shell for data to be inserted into.
        """
        h: dict     = {"horoscopes": {"sources": {}}}
        add: dict   = {}

        logging.debug("Creating data structure...")
        for source in Source:
            add = {source.name: {}}
            h["horoscopes"]["sources"].update(add)
            h["horoscopes"]["sources"][source.name].update(self.__source[source].create_source_structure())
        
        return h
    
    def __prep_data(self, data: dict) -> dict:
        """Prepares data for use.

        Args:
            data (dict): A dictionary to check and/or update.

        Returns:
            dict: A dictionary full of data and ready to use.
        """
        d: dict     = data
        if (d == {}):
            logging.debug("Data is empty. Creating structure and fetching...")
            d.update(self.__create_structure())
            d       = self.__update_all(data=d)
        else:
            d       = self.__check_data(data=d)

        logging.debug(f"Data should be ready.")
        return d
        
    def __fetch(self, horo: Horo) -> tuple[str, str]:
        """Fetch data from source.

        Args:
            horo (Horo): A prepared Horo object with information required for fetch.

        Returns:
            tuple[str, str]: A date string and horoscope text, like [date, horoscope].
        """
        logging.debug(f"Fetching horoscope: {horo.sign.full}, {horo.date}, {horo.style.full} from {horo.source.full}")
        day: Day        = Misc.get_day(date=horo.date)
        h: HoroSource   = self.__source[horo.source](sign=horo.sign, day=day, style=horo.style) # type: ignore
        return h.date, h.text
    
    def __update_day(self, 
                     day: Day,
                     source: Source,
                     style: Style,
                     data: dict) -> dict:
        """Updates data for a specified day for a specified style from a specified source.

        Args:
            day (Day): The day to update data for.
            source (Source): The source from which to update data.
            style (Style): The style to update data for.
            data (dict): The dictionary where horoscope data is held.

        Returns:
            dict: The dictionary you provided, updated.
        """
        d: dict         = data
        logging.info(f"Updating all data for {day.full} for {style.full} from {source.full}...")

        add = {day.name: {"date": "", "signs": {}}}
        d["horoscopes"]["sources"][source.name]["styles"][style.name]["days"].update(add)
        for sign in ZodiacSign:
            date_dt = Misc.get_date_from_day(day=day)
            date_str = Misc.get_date_string(date=date_dt)
            h: Horo     = Horo(sign=sign,
                               date=date_str,
                               style=style,
                               source=source)
            date, text  = self.__fetch(horo=h)
            add         = {sign.name: text}
            d["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][day.name]["signs"].update(add)
            add         = {"date": date}
            d["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][day.name].update(add)

        return d
    
    def __update_all(self, data: dict) -> dict:
        """Update all horoscopes for all styles from all sources for all days.

        Args:
            data (dict): The dictionary where horoscope data is held.

        Returns:
            dict: The dictionary you provided, updated.
        """
        d: dict = data

        for source in Source:
            for style in source.styles:
                for day in Day:
                    d = self.__update_day(day=day, source=source, style=style, data=d)
        
        return d
    
    def __move_data_day(self, 
                        start: Day,
                        dest: Day,
                        source: Source,
                        style: Style,
                        data: dict) -> dict:
        """Moves horoscopes in provided dictionary from the start and to the destination provided.

        Args:
            start (Day): The day for the horoscopes you'd like to move.
            dest (Day): The day to which the horoscopes should be moved.
            source (Source): The source that the days belong to.
            style (Style): The style that the days belong to.
            data (dict): The dictionary where horoscope data is held.

        Returns:
            dict: The dictionary you provided, updated.
        """
        d: dict             = data
        work: dict          = d["horoscopes"]["sources"][source.name]["styles"][style.name]["days"]
        logging.debug(f"Moving data from '{start.name}' to '{dest.name}' for style '{style.full}' from source '{source.full}'...") 
        start_date: str     = work[start.name]["date"]
        start_signs: dict   = work[start.name]["signs"]

        work[dest.name].update({"date": start_date})
        work[dest.name]["signs"].update(start_signs)

        d["horoscopes"]["sources"][source.name]["styles"][style.name]["days"].update(work)

        return d

    def __check_data(self, data: dict) -> dict:
        """Checks horoscope data and does what is needed to ensure it is up-to-date.

        Args:
            data (dict): The dictionary where horoscope data is held.

        Returns:
            dict: The dictionary you provided, updated.
        """
        data_in: dict               = data
        now: datetime               = Misc.get_date_from_string(string=datetime.now().strftime("%B %d, %Y"))
        dates: dict[str, datetime]  = {Day.yesterday.name   : Misc.get_date_with_offset(date=now, offset=-1),
                                       Day.today.name       : Misc.get_date_with_offset(date=now, offset=0),
                                       Day.tomorrow.name    : Misc.get_date_with_offset(date=now, offset=1)}

        # Iterate through sources
        for source in Source:
            # Iterate through styles for the source
            for style in source.styles:
                logging.info(f"Checking local data from {source.full} for {style.full}...")
                
                # Check what data thinks is tomorrow against reality
                d = data_in["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][Day.tomorrow.name]["date"]
                d_date: datetime = Misc.get_date_from_string(string=d)      # Data date
                t_date: datetime = Misc.get_date_from_day(day=Day.tomorrow) # Tomorrow date
                logging.debug(f"-Comparing local data's tomorrow date ({d_date}) to tomorrow's real date ({t_date})...")
                if (d_date == t_date):
                    logging.info("--Data is current.")
                    continue
                
                # Check what data thinks is tomorrow against what the source thinks is tomorrow
                logging.debug("Mismatch. Retrieving date from source...")
                sign = random.choice( list(ZodiacSign) ) # Get random zodiac sign to fetch source date
                h = Horo(sign=sign, date=Misc.get_date_string(dates[Day.tomorrow.name]), style=style, source=source)
                date, _ = self.__fetch(horo=h)
                s_date: datetime = Misc.get_date_from_string(string=date)   # Source date
                logging.debug(f"-Comparing source data's tomorrow date ({s_date}) to local data's tomorrow date ({d_date})...")
                if (s_date == d_date):
                    logging.info("--Data is current.") 
                    continue

                # Check if we're out by 1 day
                d_datep1: datetime = Misc.get_date_with_offset(date=d_date, offset=1)   # Data date, plus 1 day
                logging.debug(f"-Comparing source data's tomorrow date ({s_date}) to the day after local data's tomorrow date ({d_datep1})...")
                if (s_date == d_datep1):
                    # One day behind, move: today->yesterday, tomorrow->today
                    logging.info("--Data one day behind.")
                    data_in = self.__move_data_day(start=Day.today, dest=Day.yesterday, source=source, style=style, data=data_in) # move today to yesterday
                    data_in = self.__move_data_day(start=Day.tomorrow, dest=Day.today, source=source, style=style, data=data_in) # move tomorrow to today
                    
                    # Update: tomorrow
                    data_in = self.__update_day(day=Day.tomorrow, source=source, style=style, data=data_in)
                    continue
                
                # Check if we're out by 2 days
                d_datep2: datetime = Misc.get_date_with_offset(date=d_date, offset=2)   # Data date, plus 2 days
                logging.debug(f"-Comparing source data's tomorrow date ({s_date}) to two days after local data's tomorrow date ({d_datep2})...")
                if (s_date == d_datep2): 
                    # Two days behind, move: tomorrow->yesterday
                    logging.info("--Data two days behind.") 
                    data_in = self.__move_data_day(start=Day.tomorrow, dest=Day.yesterday, source=source, style=style, data=data_in) # move tomorrow to yesterday
                    
                    # Update: tomorrow + today
                    data_in = self.__update_day(day=Day.tomorrow, source=source, style=style, data=data_in)
                    data_in = self.__update_day(day=Day.today, source=source, style=style, data=data_in)
                    continue
                
                # It must all be out of date, update all
                logging.info("-All data out of date.")
                for day in Day:
                    data_in = self.__update_day(day=day, source=source, style=style, data=data_in)
            
        return data_in

    def get_horoscope(self,
                      data: dict, 
                      sign: ZodiacSign,
                      day: Day, 
                      source: Source = Source.astrology_com, 
                      style: Style = Style.daily
                      ) -> Horo:
        """Get a horoscope given specified parameters.

        Args:
            data (dict): The dictionary where horoscope data is held.
            sign (ZodiacSign): The zodiac sign for the horoscope.
            day (Day): The day for the horoscope.
            source (Source, optional): The source from which the horoscope originates. Defaults to Source.astrology_com.
            style (Style, optional): The style of the horoscope. Defaults to Style.daily.

        Returns:
            Horo: The populated Horo object.
        """
        if style not in source.styles:
            style   = source.default_style
        
        d: dict     = data
        logging.info(f"Getting {style.full} for {sign.full} for {day.full}")
        text: str   = d["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][day.name]["signs"][sign.name]
        date: str   = d["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][day.name]["date"]
        return Horo(sign=sign, date=date, source=source, style=style, text=text)

    def check_updates(self, data: dict) -> dict:
        """Check for updates to horoscope data.

        Args:
            data (dict): The dictionary where horoscope data is held.

        Returns:
            dict: The dictionary you provided, updated.
        """
        d: dict = data
        logging.info("Checking for updates...")
        d       = self.__check_data(data=d)
        logging.info("Done.")
        return d