# External
import logging
from datetime import datetime, timedelta
# Internal
from datatypes import Day, Source, Style, Horo, Zodiac
# Sources
from astrologycom import AstrologyCom

class Horoscope:
    '''Class for working with horoscopes, wraps all sources'''
    def __init__(self, data: dict) -> None:
        '''Class for working with horoscopes, wraps all sources
        :data: Dict of data'''
        self.data: dict = data
        self.data = self.__prep_data(data=self.data)

    def __create_structure(self) -> dict:
        '''Creates empty data structure. Returns dict'''
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
    
    def __prep_data(self, data: dict) -> dict:
        '''Prepares data for use. Returns dict
        :data: Dict to check and manipulate'''
        d: dict = data
        if (d == {}):
            logging.debug("Data is empty. Getting data...")
            d.update(self.__create_structure())
            d = self.update_all(data=d)
        else:
            d = self.__check_data(data=d)
        logging.debug(f"Data should be ready.")
        return d
        
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
                 data: dict, 
                 source: Source.Type = Source.astrology_com, 
                 style: Style.Type = Style.daily
                 ) -> dict:
        '''Get buffered data by day. Returns dict
        :day: Day object to get
        :data: Dict to pull from
        :source: Source for data
        :style: Style to get'''
        return data["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][day.name]
    
    def __move_data_day(self, 
                        start: Day.Type, 
                        dest: Day.Type, 
                        style: Style.Type, 
                        source: Source.Type,
                        data: dict) -> dict:
        '''Moves data in buffer, used in update operations. Returns dict
        :start: source day
        :dest: destination day
        :style: style to move
        :source: source to move
        :data: Dict to manipulate'''
        d: dict = data
        logging.debug(f"Moving data from '{start.name}' to '{dest.name}' for style '{style.full}' from source '{source.full}'...") 

        start_date: str = d["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][start.name]["date"]
        start_signs: dict = d["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][start.name]["signs"]

        d["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][dest.name].update({"date": start_date})
        d["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][dest.name]["signs"].update(start_signs)

        return d

    def __check_data(self, data: dict) -> dict:
        '''Checks data, does what is needed to ensure that data is good and up-to-date. Returns dict
        :data: Dict to check and manipulate'''
        data_in: dict = data
        Day.update_days()
        d: dict = self.__get_data_by_day(day=Day.tomorrow, data=data_in)

        d_date: datetime = datetime.strptime(d["date"], "%B %d, %Y")
        d_date_str: str = d_date.strftime('%B %d, %Y')
        t_date: datetime = Day.tomorrow.date
        t_date_str: str = t_date.strftime('%B %d, %Y')

        logging.info("Checking data...")

        logging.debug(f"Comparing local data's tomorrow date ({d_date_str}) to tomorrow's real date ({t_date_str})...")
        if (d_date_str == t_date_str): 
            logging.info("Data is current.")
            return data_in
        logging.debug("Mismatch. Retrieving date from source...")

        s: AstrologyCom = AstrologyCom(zodiac=Zodiac.aries, day=Day.tomorrow, style=Style.daily)
        s_date: datetime = datetime.strptime(s.date, "%B %d, %Y")
        s_date_str: str = s_date.strftime('%B %d, %Y')

        logging.debug(f"Comparing source data's tomorrow date ({s_date_str}) to local data's tomorrow date ({d_date_str})...")
        if (s_date_str == d_date_str): 
            # Do nothing
            logging.info("Data is current.") 
            return data_in
        
        d_datep1: datetime = d_date + timedelta(days=1)
        d_datep1_str: str = d_datep1.strftime('%B %d, %Y')

        logging.debug(f"Comparing source data's tomorrow date ({s_date_str}) to the day after local data's tomorrow date ({d_datep1_str})...")
        if (s_date_str == d_datep1_str):
            # One day behind, move: today->yesterday, tomorrow->today
            logging.info("Data one day behind.") 
            data_in = self.__move_data_day(start=Day.today, dest=Day.yesterday, style=Style.daily, source=Source.astrology_com, data=data_in) # daily, move today to yesterday
            data_in = self.__move_data_day(start=Day.today, dest=Day.yesterday, style=Style.daily_love, source=Source.astrology_com, data=data_in) # daily-love, move today to yesterday
            data_in = self.__move_data_day(start=Day.tomorrow, dest=Day.today, style=Style.daily, source=Source.astrology_com, data=data_in) # daily, move tomorrow to today
            data_in = self.__move_data_day(start=Day.tomorrow, dest=Day.today, style=Style.daily_love, source=Source.astrology_com, data=data_in) # daily-love, move tomorrow to today
            
            # Update: tomorrow
            data_in = self.__update_day(day=Day.tomorrow, source=Source.astrology_com, data=data_in)
            return data_in
        
        d_datep2: datetime = d_date + timedelta(days=2)
        d_datep2_str: str = d_datep2.strftime('%B %d, %Y')

        logging.debug(f"Comparing source data's tomorrow date ({s_date_str}) to two days after local data's tomorrow date ({d_datep2_str})...")
        if (s_date_str == d_datep2_str): 
            # Two days behind, move: tomorrow->yesterday
            logging.info("Data two days behind.") 
            data_in = self.__move_data_day(start=Day.tomorrow, dest=Day.yesterday, style=Style.daily, source=Source.astrology_com, data=data_in) # daily, move tomorrow to yesterday
            data_in = self.__move_data_day(start=Day.tomorrow, dest=Day.yesterday, style=Style.daily_love, source=Source.astrology_com, data=data_in) # daily-love, move tomorrow to yesterday
            
            # Update: tomorrow + today
            data_in = self.__update_day(day=Day.tomorrow, source=Source.astrology_com, data=data_in)
            data_in = self.__update_day(day=Day.today, source=Source.astrology_com, data=data_in)
            return data_in
        
        # All out of date, update all
        logging.info("All data out of date.") 
        data_in = self.update_all(data=data_in)
        return data_in

    def __update_day(self, day: Day.Type, source: Source.Type, data: dict) -> dict:
        '''Updates data for a specific day for all styles. Returns dict
        :day: day to update
        :source: source to update from
        :data: Dict to check and manipulate'''
        d: dict = data
        logging.info(f"Updating all data for {day.full} from {source.full}...")
        match source:
            case Source.astrology_com: #specific to Astrology.com
                for style in Style.types:
                    add = {day.name: {"date": "", "emoji": day.symbol, "signs": {}}}
                    d["horoscopes"]["sources"][source.name]["styles"][style]["days"].update(add)
                    for zodiac in Zodiac.types:
                        h = Horo(zodiac=Zodiac.types[zodiac],
                                    day=day,
                                    style=Style.types[style])
                        date, text = self.__fetch(horo=h)
                        add = {zodiac: text}
                        d["horoscopes"]["sources"][source.name]["styles"][style]["days"][day.name]["signs"].update(add)
                        add = {"date": date}
                        d["horoscopes"]["sources"][source.name]["styles"][style]["days"][day.name].update(add)
            case _: return d # This should never happen. Update loop with new source structures.
        return d

    def get_horoscope(self,
                      data: dict, 
                      zodiac: Zodiac.Type, 
                      day: Day.Type, 
                      source: Source.Type = Source.astrology_com, 
                      style: Style.Type = Style.daily
                      ) -> Horo:
        '''Get horoscope, returns Horo object
        :data: Dict to pull from
        :zodiac: Zodiac sign
        :day: Day for horoscope
        :source: Source for horoscope
        :style: horoscope style'''
        d: dict = data
        logging.info(f"Getting {style.full} for {zodiac.full} for {day.full}")
        text: str = d["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][day.name]["signs"][zodiac.name]
        return Horo(zodiac=zodiac, day=day, source=source, style=style, text=text)

    def update_all(self, data: dict) -> dict:
        '''Updates all data. Returns dict
        :data: Dict to check and manipulate'''
        d: dict = data
        logging.debug("Updating all data from sources...")
        for source in Source.types:
            match source:
                case Source.astrology_com.name: #specific to Astrology.com
                    for day in Day.types:
                        d = self.__update_day(day=Day.types[day], source=Source.types[source], data=d)
                case _: continue # This should never happen. Update loop with new source structures.
        return d

    def check_updates(self, data: dict) -> dict:
        '''Check for updates, wraps __check_data(). Returns dict
        :data: Dict to check and manipulate'''
        d: dict = data
        logging.info("Checking for updates...")
        d = self.__check_data(data=d)
        logging.info("Done.")
        return d