# External
import logging
from datetime import datetime, timedelta
# Internal
from data import Data
from datatypes import Day, Source, Style, Horo, Zodiac
# Sources
from astrologycom import AstrologyCom

class Horoscope:
    '''Class for working with horoscopes, wraps all sources'''
    def __init__(self, file: Data) -> None:
        '''Class for working with horoscopes, wraps all sources
        :file: Object where file data is held, type: Data'''
        self.file: Data = file
        self.__load_data()

    def __create_structure(self) -> dict:
        '''Creates empty data structure, returns dict'''
        h: dict = {"horoscopes": {"sources": {}}}
        add: dict = {}

        logging.debug("Creating data structure...")
        for source in Source.types:
            add = {source: {}}
            h["horoscopes"]["sources"].update(add)
            match source:
                case Source.astrology_com.name: #specific to Astrology.com
                    h["horoscopes"]["sources"][source].update(AstrologyCom.create_source_structure())
                case _: continue # This should never happen. Update loop with new source structures.
        
        return h
    
    def __load_data(self) -> None:
        if (self.file.data == {}):
            logging.debug("Data is empty. Getting data...")
            self.file.data.update(self.__create_structure())
            self.update_all()
        else:
            self.__check_data()
        logging.debug(f"Data should be ready in file: {self.file.path}")
        
    def __fetch(self, horo: Horo) -> tuple[str, str]:
        '''Fetch data from source, return date + text
        :horo: Horo object'''
        match horo.source:
            case Source.astrology_com:
                logging.debug(f"Fetching horoscope: {horo.zodiac.name}, {horo.day.date.strftime('%Y-%m-%d')}, {horo.style.name} from {horo.source.name}")
                h = AstrologyCom(zodiac=horo.zodiac, day=horo.day, style=horo.style)
                return h.date, h.text
            case _: return "", "Unknown Source" # This should never happen. Update loop with new sources.
    
    def __get_data_by_day(self,  
                 day: Day.Type, 
                 source: Source.Type = Source.astrology_com, 
                 style: Style.Type = Style.daily,
                 ) -> dict:
        '''Get buffered data by day, returns dict
        :day: Day object to get
        :source: Source for data
        :style: Style to get'''
        return self.file.data["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][day.name]
    
    def __move_data_day(self, 
                        start: Day.Type, 
                        dest: Day.Type, 
                        style: Style.Type, 
                        source: Source.Type) -> None:
        '''Moves data in buffer, used in update operations
        :start: source day
        :dest: destination day
        :style: style to move
        :source: source to move'''
        logging.debug(f"Moving data from '{start.name}' to '{dest.name}' for style '{style.full}' from source '{source.full}'...") 

        start_date: str = self.file.data["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][start.name]["date"]
        start_signs: dict = self.file.data["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][start.name]["signs"]

        self.file.data["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][dest.name].update({"date": start_date})
        self.file.data["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][dest.name]["signs"].update(start_signs)

    def __check_data(self) -> None:
        '''Checks data, does what is needed to ensure that data is good and up-to-date'''
        Day.update_days()
        self.file.load_data()
        d: dict = self.__get_data_by_day(day=Day.tomorrow)

        d_date: datetime = datetime.strptime(d["date"], "%B %d, %Y")
        d_date_str: str = d_date.strftime('%B %d, %Y')
        t_date: datetime = Day.tomorrow.date
        t_date_str: str = t_date.strftime('%B %d, %Y')

        logging.info("Checking data...")

        logging.debug(f"Comparing local data's tomorrow date ({d_date_str}) to tomorrow's real date ({t_date_str})...")
        if (d_date_str == t_date_str): 
            logging.info("Data is current.")
            return
        logging.debug("Mismatch. Retrieving date from source...")

        s: AstrologyCom = AstrologyCom(zodiac=Zodiac.aries, day=Day.tomorrow, style=Style.daily)
        s_date: datetime = datetime.strptime(s.date, "%B %d, %Y")
        s_date_str: str = s_date.strftime('%B %d, %Y')

        logging.debug(f"Comparing source data's tomorrow date ({s_date_str}) to local data's tomorrow date ({d_date_str})...")
        if (s_date_str == d_date_str): 
            # Do nothing
            logging.info("Data is current.") 
            return
        
        d_datep1: datetime = d_date + timedelta(days=1)
        d_datep1_str: str = d_datep1.strftime('%B %d, %Y')

        logging.debug(f"Comparing source data's tomorrow date ({s_date_str}) to the day after local data's tomorrow date ({d_datep1_str})...")
        if (s_date_str == d_datep1_str):
            # One day behind, move: today->yesterday, tomorrow->today
            logging.info("Data one day behind.") 
            self.__move_data_day(start=Day.today, dest=Day.yesterday, style=Style.daily, source=Source.astrology_com) # daily, move today to yesterday
            self.__move_data_day(start=Day.today, dest=Day.yesterday, style=Style.daily_love, source=Source.astrology_com) # daily-love, move today to yesterday
            self.__move_data_day(start=Day.tomorrow, dest=Day.today, style=Style.daily, source=Source.astrology_com) # daily, move tomorrow to today
            self.__move_data_day(start=Day.tomorrow, dest=Day.today, style=Style.daily_love, source=Source.astrology_com) # daily-love, move tomorrow to today
            
            # Update: tomorrow
            self.__update_day(day=Day.tomorrow, source=Source.astrology_com)
            return
        
        d_datep2: datetime = d_date + timedelta(days=2)
        d_datep2_str: str = d_datep2.strftime('%B %d, %Y')

        logging.debug(f"Comparing source data's tomorrow date ({s_date_str}) to two days after local data's tomorrow date ({d_datep2_str})...")
        if (s_date_str == d_datep2_str): 
            # Two days behind, move: tomorrow->yesterday
            logging.info("Data two days behind.") 
            self.__move_data_day(start=Day.tomorrow, dest=Day.yesterday, style=Style.daily, source=Source.astrology_com) # daily, move tomorrow to yesterday
            self.__move_data_day(start=Day.tomorrow, dest=Day.yesterday, style=Style.daily_love, source=Source.astrology_com) # daily-love, move tomorrow to yesterday
            
            # Update: tomorrow + today
            self.__update_day(day=Day.tomorrow, source=Source.astrology_com)
            self.__update_day(day=Day.today, source=Source.astrology_com)
            return
        
        # All out of date, update all
        logging.info("All data out of date.") 
        self.update_all()
        return

    def __update_day(self, day: Day.Type, source: Source.Type) -> None:
        '''Updates data for a specific day for all styles, writes buffer to data source
        :day: day to update
        :source: source to update from'''
        logging.info(f"Updating all data for {day.full} from {source.full}...")
        match source:
            case Source.astrology_com: #specific to Astrology.com
                for style in Style.types:
                    add = {day.name: {"date": "", "emoji": day.symbol, "signs": {}}}
                    self.file.data["horoscopes"]["sources"][source.name]["styles"][style]["days"].update(add)
                    for zodiac in Zodiac.types:
                        h = Horo(zodiac=Zodiac.types[zodiac],
                                    day=day,
                                    style=Style.types[style])
                        date, text = self.__fetch(horo=h)
                        add = {zodiac: text}
                        self.file.data["horoscopes"]["sources"][source.name]["styles"][style]["days"][day.name]["signs"].update(add)
                        add = {"date": date}
                        self.file.data["horoscopes"]["sources"][source.name]["styles"][style]["days"][day.name].update(add)
            case _: return # This should never happen. Update loop with new source structures.
        self.file.write_data()

    def get_horoscope(self, 
                 zodiac: Zodiac.Type, 
                 day: Day.Type, 
                 source: Source.Type = Source.astrology_com, 
                 style: Style.Type = Style.daily,
                 ) -> Horo:
        '''Get horoscope, returns Horo object
        :zodiac: Zodiac sign
        :day: Day for horoscope
        :source: Source for horoscope
        :style: horoscope style'''
        self.file.load_data()
        logging.info(f"Getting {style.full} for {zodiac.full} for {day.full}")
        text: str = self.file.data["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][day.name]["signs"][zodiac.name]
        return Horo(zodiac=zodiac, day=day, source=source, style=style, text=text)

    def update_all(self) -> None:
        '''Updates all data, writes buffer to data source'''
        logging.debug("Updating all data from sources...")
        for source in Source.types:
            match source:
                case Source.astrology_com.name: #specific to Astrology.com
                    for day in Day.types:
                        self.__update_day(day=Day.types[day], source=Source.types[source])
                case _: continue # This should never happen. Update loop with new source structures.
        self.file.write_data()

    def check_updates(self) -> None:
        '''Check for updates, wraps __check_data()'''
        logging.info("Checking for updates...")
        self.__check_data()
        logging.info("Done.")