# External
from datetime import datetime, timedelta
# Internal
from astrobot.core.datatypes import Day


format: str = "%B %d, %Y"

class Misc:
    """Miscellaneous static functions.
    """
    @staticmethod
    def get_date_from_day(day: Day) -> datetime:
        """Get datetime without time.

        Args:
            day (Day): Relative day from Day

        Returns:
            datetime: datetime object
        """
        d = datetime.today() + timedelta(days=day.value)
        d_str = datetime.strftime(d, format)
        fin = datetime.strptime(d_str, format)

        return fin
    
    @staticmethod
    def get_day_of_week_from_day(day: Day) -> str:
        """Get the day of the week from a given relative Day object.

        Args:
            day (Day): _description_

        Returns:
            str: _description_
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
        return datetime.strptime(string, format)
    
    @staticmethod
    def get_date_string(date: datetime) -> str:
        """Get date string from datetime.

        Args:
            date (datetime): Datetime object to turn into a string.

        Returns:
            str: String, formatted "%B %d, %Y". e.g. "July 04, 1776"
        """
        return date.strftime(format)
    
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
        datestr: str = datetime.strptime(date, format).strftime(format)

        class Date:
            yesterday: str  = Misc.get_date_from_day(day=Day.yesterday).strftime(format)
            today: str      = Misc.get_date_from_day(day=Day.today).strftime(format)
            tomorrow: str   = Misc.get_date_from_day(day=Day.tomorrow).strftime(format)

        match datestr:
            case Date.today:
                return Day.today
            case Date.tomorrow:
                return Day.tomorrow
            case Date.yesterday:
                return Day.yesterday
            case _:
                return Day.today