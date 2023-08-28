# External
from datetime import datetime, timedelta
# Internal
from astrobot.core.datatypes import Day

class Misc:
    '''Class with miscellaneous static methods'''

    @staticmethod
    def get_date_from_day(day: Day.Type) -> datetime:
        '''Get datetime without time. Returns datetime
        :day: Day.Type object for relative day'''
        offset: dict[Day.Type, int] = {Day.yesterday: -1,
                                       Day.today    : 0,
                                       Day.tomorrow : 1}

        d = datetime.today() + timedelta(days=offset[day])
        d_str = datetime.strftime(d, "%B %d, %Y")
        fin = datetime.strptime(d_str, "%B %d, %Y")

        return fin
    
    @staticmethod
    def get_date_from_string(string: str) -> datetime:
        '''Get datetime without time from string. Returns datetime
        :string: Date string'''
        return datetime.strptime(string, "%B %d, %Y")
    
    @staticmethod
    def get_date_string(date: datetime) -> str:
        '''Get date string from datetime. Returns str
        :date: datetime'''
        return date.strftime("%B %d, %Y")
    
    @staticmethod
    def get_date_with_offset(date: datetime, offset: int) -> datetime:
        '''Get datetime with offset. Returns datetime
        :date: Starting datetime
        :offset: Offset in number of days'''
        return date + timedelta(days=offset)
    
    @staticmethod
    def get_day(date: str) -> Day.Type:
        '''Get day from string. Returns Day.Type
        :date: date string'''
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