# External
import logging
from datetime import datetime, timedelta
# Internal
from astrobot.core.datatypes import Day, Source, Style, Horo, Zodiac
# Sources
from astrobot.modules.sources.astrologycom import AstrologyCom
from astrobot.modules.sources.astrostyle import Astrostyle


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
            add = {Source.types[source].name: {}}
            h["horoscopes"]["sources"].update(add)
            match source:
                case Source.astrology_com.name: # specific to Astrology.com
                    h["horoscopes"]["sources"][source].update(AstrologyCom.create_source_structure())
                case Source.astrostyle.name: # specific to AstroStyle
                    h["horoscopes"]["sources"][source].update(Astrostyle.create_source_structure())
                case _: continue # This should never happen. Update loop with new source structures.
        
        return h
    
    def __prep_data(self, data: dict) -> dict:
        '''Prepares data for use. Returns dict
        :data: Dict to check and manipulate'''
        d: dict = data
        if (d == {}):
            logging.debug("Data is empty. Creating structure...")
            d.update(self.__create_structure())
        
        d = self.__check_data(data=d)
        logging.debug(f"Data should be ready.")
        return d
        
    def __fetch(self, horo: Horo) -> tuple[str, str]:
        '''Fetch data from source, return date + text
        :horo: Horo object'''
        logging.debug(f"Fetching horoscope: {horo.zodiac.name}, {horo.date}, {horo.style.name} from {horo.source.name}")
        
        day = self.get_day(date=horo.date)

        match horo.source:
            case Source.astrology_com:             
                h = AstrologyCom(zodiac=horo.zodiac, day=day, style=horo.style)
                return h.date, h.text
            case Source.astrostyle:
                h = Astrostyle(zodiac=horo.zodiac, day=day, style=horo.style)
                return h.date, h.text
            case _: return "", "Unknown Source" # This should never happen. Update loop with new sources.    
    
    def __move_data_day(self, 
                        start: Day.Type,
                        dest: Day.Type,
                        source: Source.Type,
                        style: Style.Type,
                        data: dict) -> dict:
        '''Moves data in buffer, used in update operations. Returns dict
        :start: source day
        :dest: destination day
        :source: source to move
        :style: style to move
        :data: Dict to manipulate'''
        d: dict = data

        work: dict = d["horoscopes"]["sources"][source.name]["styles"][style.name]["days"]
        
        logging.debug(f"Moving data from '{start.name}' to '{dest.name}' for style '{style.full}' from source '{source.full}'...") 

        start_date: str = work[start.name]["date"]
        start_signs: dict = work[start.name]["signs"]

        work[dest.name].update({"date": start_date})
        work[dest.name]["signs"].update(start_signs)

        d["horoscopes"]["sources"][source.name]["styles"][style.name]["days"].update(work)

        return d

    def __check_data(self, data: dict) -> dict:
        '''Checks data, does what is needed to ensure that data is good and up-to-date. Returns dict
        :data: Dict to check and manipulate'''
        data_in: dict = data
        Day.update_days()

        for _, source in Source.types.items():
            for style in source.styles:
                logging.debug(f"Checking local data from {source.full} for {style.full}...")
                # Check what data thinks is tomorrow against reality
                d = data_in["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][Day.tomorrow.name]["date"]
                d_date: datetime = datetime.strptime(str(d), "%B %d, %Y")           # Data date
                t_date: datetime = datetime.strptime(Day.tomorrow.ymd, "%B %d, %Y") # Tomorrow date
                logging.debug(f"Comparing local data's tomorrow date ({d_date}) to tomorrow's real date ({t_date})...")
                if (d_date == t_date):
                    logging.info("Data is current.")
                    continue
                
                # Check what data thinks is tomorrow against what the source thinks is tomorrow
                logging.debug("Mismatch. Retrieving date from source...")
                h = Horo(zodiac=Zodiac.aries, date=Day.tomorrow.ymd, style=style, source=source)
                date, _ = self.__fetch(horo=h)
                s_date = datetime.strptime(date, "%B %d, %Y") # Source date
                logging.debug(f"Comparing source data's tomorrow date ({s_date}) to local data's tomorrow date ({d_date})...")
                if (s_date == d_date):
                    logging.info("Data is current.") 
                    continue

                # Check if we're out by 1 day
                d_datep1: datetime = d_date + timedelta(days=1) # Data date, plus 1 day
                logging.debug(f"Comparing source data's tomorrow date ({s_date}) to the day after local data's tomorrow date ({d_datep1})...")
                if (s_date == d_datep1):
                    # One day behind, move: today->yesterday, tomorrow->today
                    logging.info("Data one day behind.") 
                    data_in = self.__move_data_day(start=Day.today, dest=Day.yesterday, source=source, style=style, data=data_in) # move today to yesterday
                    data_in = self.__move_data_day(start=Day.tomorrow, dest=Day.today, source=source, style=style, data=data_in) # move tomorrow to today
                    
                    # Update: tomorrow
                    data_in = self.__update_day(day=Day.tomorrow, source=source, style=style, data=data_in)
                
                # Check if we're out by 2 days
                d_datep2: datetime = d_date + timedelta(days=2) # Data date, plus 2 days
                logging.debug(f"Comparing source data's tomorrow date ({s_date}) to two days after local data's tomorrow date ({d_datep2})...")
                if (s_date == d_datep2): 
                    # Two days behind, move: tomorrow->yesterday
                    logging.info("Data two days behind.") 
                    data_in = self.__move_data_day(start=Day.tomorrow, dest=Day.yesterday, source=source, style=style, data=data_in) # move tomorrow to yesterday
                    
                    # Update: tomorrow + today
                    data_in = self.__update_day(day=Day.tomorrow, source=source, style=style, data=data_in)
                    data_in = self.__update_day(day=Day.today, source=source, style=style, data=data_in)
                
                # It must all be out of date, update all
                logging.info("All data out of date.")
                data_in = self.__update_day(day=Day.tomorrow, source=source, style=style, data=data_in)
                data_in = self.__update_day(day=Day.today, source=source, style=style, data=data_in)
                data_in = self.__update_day(day=Day.yesterday, source=source, style=style, data=data_in)
            
        return data_in

    def __update_day(self, day: Day.Type,
                     source: Source.Type,
                     style: Style.Type,
                     data: dict) -> dict:
        '''Updates data for a specific day for all styles. Returns dict
        :day: day to update
        :source: source to update from
        :data: Dict to check and manipulate'''
        d: dict = data
        logging.info(f"Updating all data for {day.full}...")

        add = {day.name: {"date": "", "emoji": day.symbol, "signs": {}}}
        d["horoscopes"]["sources"][source.name]["styles"][style.name]["days"].update(add)
        for _, zodiac in Zodiac.types.items():
            h = Horo(zodiac=zodiac,
                        date=day.ymd,
                        style=style,
                        source=source)
            date, text = self.__fetch(horo=h)
            add = {zodiac.name: text}
            d["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][day.name]["signs"].update(add)
            add = {"date": date}
            d["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][day.name].update(add)

        return d

    def get_day(self, date: str) -> Day.Type:
        datestr: str = datetime.strptime(date, "%B %d, %Y").strftime('%B %d, %Y')

        class Date:
            tomorrow: str = Day.tomorrow.date.strftime('%B %d, %Y')
            today: str = Day.today.date.strftime('%B %d, %Y')
            yesterday: str = Day.yesterday.date.strftime('%B %d, %Y')

        match datestr:
            case Date.today:
                return Day.today
            case Date.tomorrow:
                return Day.tomorrow
            case Date.yesterday:
                return Day.yesterday
            case _:
                return Day.today

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
        if style not in source.styles:
            style = Style.daily
        
        d: dict = data
        logging.info(f"Getting {style.full} for {zodiac.full} for {day.full}")
        text: str = d["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][day.name]["signs"][zodiac.name]
        date: str = d["horoscopes"]["sources"][source.name]["styles"][style.name]["days"][day.name]["date"]
        return Horo(zodiac=zodiac, date=date, source=source, style=style, text=text)

    def check_updates(self, data: dict) -> dict:
        '''Check for updates, wraps __check_data(). Returns dict
        :data: Dict to check and manipulate'''
        d: dict = data
        logging.info("Checking for updates...")
        d = self.__check_data(data=d)
        logging.info("Done.")
        return d