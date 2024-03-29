# External
from datetime import datetime, timedelta
# Internal
from astrobot.modules.common import Day


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
    def get_day_of_week_from_string(string: str) -> str:
        """Get the day of the week from string.

        Args:
            string (str): Time string to format

        Returns:
            str: A lowercase string for the day of the week.
        """
        dt: datetime = datetime.strptime(string, Misc.date_format)
        return dt.strftime("%A").lower()
    
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

        date_match: dict[str, Day]  = {Date.yesterday:  Day.yesterday,
                                       Date.today:      Day.today,
                                       Date.tomorrow:   Day.tomorrow}
        
        try:
            ret = date_match[datestr]
        except KeyError:
            ret = Day.today
        
        return ret