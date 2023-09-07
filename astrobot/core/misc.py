# External
from datetime import datetime, timedelta
# Internal
from astrobot.core.datatypes import Day


class Misc:
    """Miscellaneous static functions.
    """
    @staticmethod
    def get_date_from_day(day: Day.Type) -> datetime:
        """Get datetime without time.

        Args:
            day (Day.Type): Relative day from Day.Type

        Returns:
            datetime: datetime object
        """
        offset: dict[Day.Type, int] = {Day.yesterday: -1,
                                       Day.today    : 0,
                                       Day.tomorrow : 1}

        d = datetime.today() + timedelta(days=offset[day])
        d_str = datetime.strftime(d, "%B %d, %Y")
        fin = datetime.strptime(d_str, "%B %d, %Y")

        return fin
    
    @staticmethod
    def get_date_from_string(string: str) -> datetime:
        """Get datetime without time from string.

        Args:
            string (str): Time string to format

        Returns:
            datetime: datetime object, time 00:00
        """
        return datetime.strptime(string, "%B %d, %Y")
    
    @staticmethod
    def get_date_string(date: datetime) -> str:
        """Get date string from datetime.

        Args:
            date (datetime): Datetime object to turn into a string.

        Returns:
            str: String, formatted "%B %d, %Y". e.g. "July 04, 1776"
        """
        return date.strftime("%B %d, %Y")
    
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
    def get_day(date: str) -> Day.Type:
        """Get day from string.

        Args:
            date (str): Date string.

        Returns:
            Day.Type: Day object.
        """
        datestr: str = datetime.strptime(date, "%B %d, %Y").strftime('%B %d, %Y')

        class Date:
            yesterday: str  = Misc.get_date_from_day(day=Day.yesterday).strftime('%B %d, %Y')
            today: str      = Misc.get_date_from_day(day=Day.today).strftime('%B %d, %Y')
            tomorrow: str   = Misc.get_date_from_day(day=Day.tomorrow).strftime('%B %d, %Y')

        match datestr:
            case Date.today:
                return Day.today
            case Date.tomorrow:
                return Day.tomorrow
            case Date.yesterday:
                return Day.yesterday
            case _:
                return Day.today