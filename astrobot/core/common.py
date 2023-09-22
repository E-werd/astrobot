# External
import json, logging
from enum import Enum
from datetime import datetime, timedelta
# Internal
from astrobot.modules.sources.common import Day

    
class DataSource(Enum):
    """Enum for possible data sources.
    """
    json = "JSON data"

    @property
    def full(self) -> str:
        return self.value

class Data:
    """Class for accessing and manipulating data
    """
    def __init__(self, file: str, source: DataSource) -> None:
        """Class for accessing and manipulating data.

        Args:
            file (str): The file path where data is stored as a string.
            source (DataSource): The source data type.
        """
        self.path: str                  = file
        self.source: DataSource         = source

    def __load_data(self) -> dict:
        """Wraps buffering of data from any source.

        Returns:
            dict: A dict containing data from source.
        """
        match self.source:
            case DataSource.json:
                return self.__load_json()
            case _: return {} # This should never happen. Update loop with new data sources.

    def __load_json(self) -> dict:
        """Buffers JSON from self.path.

        Returns:
            dict: A dict containing data from source.
        """
        try:
            logging.info(f"Loading data from file: {self.path}")
            with open(file=self.path, mode="r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"*** File load error: {str(e)}")
            logging.warning(f"Assuming file is empty or missing, returning empty dataset.")
            return {}

    def __write_json(self, data: dict) -> None:
        """Writes JSON to self.path from self.data.

        Args:
            data (dict): A dict containing data.
        """
        try:
            logging.info(f"Writing data to file: {self.path}")
            with open(file=self.path, mode='w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"*** File write error: {str(e)}")

    def load_data(self) -> dict:
        """Wraps __load_data(), loads data from source specified at instantiation.

        Returns:
            dict: A dict containing data from source.
        """
        return self.__load_data()

    def write_data(self, data: dict) -> None:
        """Write data back to source file.

        Args:
            data (dict): A dict containing data.
        """
        match self.source:
            case DataSource.json: 
                self.__write_json(data=data)
            case _: 
                pass # This should never happen. Update loop with new data sources.

class Misc:
    """Miscellaneous static functions.
    """
    date_format: str = "%B %d, %Y"

    @staticmethod
    def get_date_from_day(day: Day) -> datetime:
        """Get datetime without time.

        Args:
            day (Day): Relative day from Day

        Returns:
            datetime: datetime object
        """
        d = datetime.today() + timedelta(days=day.value)
        d_str = datetime.strftime(d, Misc.date_format)
        fin = datetime.strptime(d_str, Misc.date_format)

        return fin
    
    @staticmethod
    def get_day_of_week_from_day(day: Day) -> str:
        """Get the day of the week from a given relative Day object.

        Args:
            day (Day): Relative day from Day

        Returns:
            str: A lowercase string for the day of the week.
        """
        date = Misc.get_date_from_day(day=day)
        return date.strftime("%A").lower()
    
    @staticmethod
    def get_date_from_string(string: str) -> datetime:
        """Get datetime without time from string.

        Args:
            string (str): Time string to format

        Returns:
            datetime: datetime object, time 00:00
        """
        return datetime.strptime(string, Misc.date_format)
    
    @staticmethod
    def get_date_string(date: datetime) -> str:
        """Get date string from datetime.

        Args:
            date (datetime): Datetime object to turn into a string.

        Returns:
            str: String, formatted "%B %d, %Y". e.g. "July 04, 1776"
        """
        return date.strftime(Misc.date_format)
    
    @staticmethod
    def get_date_with_offset(date: datetime, offset: int) -> datetime:
        """Get datetime with offset.

        Args:
            date (datetime): Datetime object to offset
            offset (int): Offset, number of days

        Returns:
            datetime: Datetime object, give or take the offset.
        """
        return date + timedelta(days=offset)
    
    @staticmethod
    def get_day(date: str) -> Day:
        """Get day from string.

        Args:
            date (str): Date string.

        Returns:
            Day: Day object.
        """
        datestr: str = datetime.strptime(date, Misc.date_format).strftime(Misc.date_format)

        class Date:
            yesterday: str  = Misc.get_date_from_day(day=Day.yesterday).strftime(Misc.date_format)
            today: str      = Misc.get_date_from_day(day=Day.today).strftime(Misc.date_format)
            tomorrow: str   = Misc.get_date_from_day(day=Day.tomorrow).strftime(Misc.date_format)

        match datestr:
            case Date.today:
                return Day.today
            case Date.tomorrow:
                return Day.tomorrow
            case Date.yesterday:
                return Day.yesterday
            case _:
                return Day.today