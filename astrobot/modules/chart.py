# External
import logging
from enum import Enum
from datetime import datetime
from geopy.geocoders import HereV7
from timezonefinder import TimezoneFinder
import pycountry
from kerykeion import AstrologicalSubject, NatalAspects, KerykeionPointModel
from prettytable import PrettyTable
import pandas as pd
# Internal
from astrobot.core.astrology import ZodiacSign

    
class Table(Enum):
    """Defines table types and their columns.
    """
    planets     = ["Planet", "Sign", "Position", "House"]
    houses      = ["House", "Sign", "Position"]
    aspects     = ["Planet 1", "Aspect", "Planet 2"]
    elements    = ["Element", "Count"]
    modes       = ["Modality", "Count"]

    @property
    def columns(self):
        """Columns for table generation.

        Returns:
            list[str]: A list of strings representing table columns.
        """
        return self.value

class GeoLookup:
    """Look up information about a location.

    Returns:
        GeoLookup: A GeoLookup object.
    """
    def __init__(self, geo_api: str, query: str) -> None:
        """Look up information about a location.

        Args:
            geo_api (str): API key for Geocoder.
            query (str): A lookup string, e.g. "New York City", "Paris, France"
        """
        ## Get raw data from Here
        geo_apikey: str        = geo_api
        self.raw: dict          = self.__lookup(api_key=geo_apikey, query=query)

        ## Set lat/lon and location names
        self.latitude: float    = float( self.raw["position"]["lat"] )
        self.longitude: float   = float( self.raw["position"]["lng"] )
        self.city: str          = self.raw["address"]["city"]

        # Get locale and translate to 2-letter country name
        locale: str             = self.raw["address"]["countryCode"]
        country_obj             = pycountry.countries.get(alpha_3=locale)
        self.country: str       = country_obj.alpha_2
        
        # Get timezone from coords
        self.timezone: str      = self.__get_tz(lat=self.latitude, lon=self.longitude)

    def __lookup(self, api_key: str, query: str) -> dict:
        """Perform lookup on location string.

        Args:
            api_key (str): API key for Here.
            query (str): A lookup string, e.g. "New York City", "Paris, France"

        Returns:
            dict: A dictionary of raw data, derived from JSON response.
        """
        geo: HereV7 = HereV7(apikey=api_key)
        location    = geo.geocode(query=query, exactly_one=True)
        return location.raw # type: ignore
    
    def __get_tz(self, lat: float, lon: float) -> str:
        """Perform timezone lookup from coordinates.

        Args:
            lat (float): Latitude of location
            lon (float): Longitude of location

        Returns:
            str: Timezone as a string, e.g. "America/New_York", "Europe/Paris"
        """
        tf: TimezoneFinder  = TimezoneFinder()
        tz: str             = str( tf.timezone_at(lat=lat, lng=lon) )
        return tz

class ChartUser:
    """Object containing data and methods used to generate astrological charts.

    Returns:
        ChartUser: A ChartUser object.
    """
    kery_signs: dict[str, ZodiacSign]   = {"Ari":   ZodiacSign.aries,
                                           "Tau":   ZodiacSign.taurus,
                                           "Gem":   ZodiacSign.gemini,
                                           "Can":   ZodiacSign.cancer,
                                           "Leo":   ZodiacSign.leo,
                                           "Vir":   ZodiacSign.virgo,
                                           "Lib":   ZodiacSign.libra,
                                           "Sco":   ZodiacSign.scorpio,
                                           "Sag":   ZodiacSign.sagittarius,
                                           "Cap":   ZodiacSign.capricorn,
                                           "Aqu":   ZodiacSign.aquarius,
                                           "Pis":   ZodiacSign.pisces}
    housename: dict[str, str]           = {"First_House":       "1st (ASC)",
                                           "Second_House":      "2nd",
                                           "Third_House":       "3rd",
                                           "Fourth_House":      "4th",
                                           "Fifth_House":       "5th",
                                           "Sixth_House":       "6th",
                                           "Seventh_House":     "7th",
                                           "Eighth_House":      "8th",
                                           "Ninth_House":       "9th",
                                           "Tenth_House":       "10th (MC)",
                                           "Eleventh_House":    "11th",
                                           "Twelfth_House":     "12th"}

    def __init__(self, geo_api: str, name: str, location: str, birthday: str, time: str = "00:00") -> None:
        """Object containing data and methods used to generate astrological charts.

        Args:
            geo_api (str): API key for Geocoder, used by GeoLookup class.
            name (str): Name of subject.
            location (str): Location of subject.
            birthday (str): Birthday of subject.
            time (_type_, optional): Birth time of subject in 24-hour format. Defaults to "00:00".
        """
        # Set name of subject
        self.name: str              = name
        
        # Get data from Here, set location variables
        lookup: GeoLookup           = GeoLookup(geo_api=geo_api, query=location)
        self.latitude: float        = lookup.latitude
        self.longitude: float       = lookup.longitude
        self.city: str              = lookup.city
        self.country: str           = lookup.country
        self.timezone: str          = lookup.timezone
        
        # Create datetime object, split out into individual parts
        birthdate: datetime         = datetime.strptime(f"{birthday} {time}", "%m/%d/%Y %H:%M")
        self.year: int              = birthdate.year
        self.month: int             = birthdate.month
        self.day: int               = birthdate.day
        self.hour: int              = birthdate.hour
        self.minute: int            = birthdate.minute
        
        # Build iterator for chart data
        subject: AstrologicalSubject = self.__make_subject()
        self.planets: dict[str, KerykeionPointModel]    = {"Sun":          subject.sun, #type: ignore
                                                           "Moon":         subject.moon,
                                                           "Mercury":      subject.mercury,
                                                           "Venus":        subject.venus,
                                                           "Mars":         subject.mars,
                                                           "Jupiter":      subject.jupiter,
                                                           "Saturn":       subject.saturn,
                                                           "Uranus":       subject.uranus,
                                                           "Neptune":      subject.neptune,
                                                           "Pluto":        subject.pluto,
                                                           "Mean_Node":    subject.mean_node,
                                                           "True_Node":    subject.true_node,
                                                           "Chiron":       subject.chiron,
                                                           "Mean_Lilith":  subject.mean_lilith}
        self.houses: dict[str, KerykeionPointModel]     =  {"First_House":       subject.first_house,
                                                            "Second_House":      subject.second_house,
                                                            "Third_House":       subject.third_house,
                                                            "Fourth_House":      subject.fourth_house,
                                                            "Fifth_House":       subject.fifth_house,
                                                            "Sixth_House":       subject.sixth_house,
                                                            "Seventh_House":     subject.seventh_house,
                                                            "Eighth_House":      subject.eighth_house,
                                                            "Ninth_House":       subject.ninth_house,
                                                            "Tenth_House":       subject.tenth_house,
                                                            "Eleventh_House":    subject.eleventh_house,
                                                            "Twelfth_House":     subject.twelfth_house}
        self.build_data: dict[Table, pd.DataFrame]      = {Table.houses:    self.__build_house_data(subject=subject),
                                                           Table.planets:   self.__build_planet_data(subject=subject),
                                                           Table.elements:  self.__build_element_data(subject=subject),
                                                           Table.modes:     self.__build_mode_data(subject=subject),
                                                           Table.aspects:   self.__build_aspects_data(subject=subject)}

    def __make_subject(self) -> AstrologicalSubject:
        """Gets an AstrologicalSubject object based on data from ChartUser.

        Returns:
            AstrologicalSubject: Kerykeion object containing all calculations.
        """
        return AstrologicalSubject(name=self.name, 
                                   year=self.year, 
                                   month=self.month, 
                                   day=self.day, 
                                   hour=self.hour, 
                                   minute=self.minute,  
                                   lat=self.latitude, 
                                   lng=self.longitude, 
                                   tz_str=self.timezone,
                                   city=self.city,
                                   nation=self.country,
                                   online=False)
    
    def __build_house_data(self, subject: AstrologicalSubject) -> pd.DataFrame:
        """Build DataFrame object for the houses table.

        Args:
            subject (AstrologicalSubject): Kerykeion object containing all calculations.

        Returns:
            pd.DataFrame: A pandas DataFrame object.
        """
        # Setup column lists
        houses: list[str]       = []
        signs: list[str]        = []
        positions: list[str]    = []

        for house in subject.houses_names_list:
            # Set retrograde
            ret: str = ""
            if self.houses[house].retrograde:
                ret  = " R"

            # Set data for row
            sign: ZodiacSign    = ChartUser.kery_signs[self.houses[house].sign]
            sname: str          = sign.symbol + " " + sign.full
            pname: str          = str("{:.2f}".format(self.houses[house].position)) + "°" + ret

            # Assign data to row
            houses.append(ChartUser.housename[self.houses[house].name])
            signs.append(sname)
            positions.append(pname)
        
        # Create and return DataFrame
        df = pd.DataFrame({'House':houses,'Sign':signs, 'Position': positions})
        return df
    
    def __build_planet_data(self, subject: AstrologicalSubject) -> pd.DataFrame:
        """Build DataFrame object for the planets table.

        Args:
            subject (AstrologicalSubject): Kerykeion object containing all calculations.

        Returns:
            pd.DataFrame: A pandas DataFrame object.
        """
        # Setup column lists
        planets: list   = []
        signs: list     = []
        positions: list = []
        houses: list    = []
        
        for planet in subject.planets_names_list:
            # Skip unwanted planets
            if planet == "Mean_Node":
                continue

            # Set retrograde
            ret: str = ""
            if self.planets[planet].retrograde:
                ret = " R"

            # Filter and rename planet names for Planet
            pname: str = ""
            if planet == "True_Node":
                pname = "N Node"
            else:
                pname = planet
            
            # Prepare strings
            sign         = ChartUser.kery_signs[self.planets[planet].sign]
            sname: str   = sign.symbol + " " + sign.full
            posname: str = str("{:.2f}".format(self.planets[planet].position)) + "°" + ret
            hname: str   = ChartUser.housename[str(self.planets[planet].house)]

            # Assign data to row
            planets.append(pname)
            signs.append(sname)
            positions.append(posname)
            houses.append(hname)

        # Create and return DataFrame
        df = pd.DataFrame({'Planet':planets,'Sign':signs, 'Position': positions, 'House':houses})
        return df

    def __build_element_data(self, subject: AstrologicalSubject) -> pd.DataFrame:
        """Build DataFrame object for the elements table.

        Args:
            subject (AstrologicalSubject): Kerykeion object containing all calculations.

        Returns:
            pd.DataFrame: A pandas DataFrame object.
        """
        # Setup column lists
        elements: list = []
        counts: list  = []

        # Setup count dictionary
        element_list: dict[str, int] = {"Air":      0,
                                        "Fire":     0,
                                        "Earth":    0,
                                        "Water":    0}

        # Iterate through planets
        for planet in subject.planets_names_list:
            # Skip unwanted planets
            if planet == "Mean_Node":
                continue

            # Increment count for element
            element_list[self.planets[planet].element] += 1

        # Iterate through elements, assign data to row
        for element, count in element_list.items():
            elements.append(element)
            counts.append(str(count))

        # Create and return DataFrame
        df = pd.DataFrame({"Element": elements, "Count": counts})
        return df
    
    def __build_mode_data(self, subject: AstrologicalSubject) -> pd.DataFrame:
        """Build DataFrame object for the modes table.

        Args:
            subject (AstrologicalSubject): Kerykeion object containing all calculations.

        Returns:
            pd.DataFrame: A pandas DataFrame object.
        """
        # Setup column lists
        modes: list = []
        counts: list = []
        
        # Setup count dictionary
        modality: dict[str, int] = {"Cardinal": 0,
                                    "Fixed":    0,
                                    "Mutable":  0}
        
        # Iterate through planets
        for planet in subject.planets_names_list:
            # Skip unwanted planets
            if planet == "Mean_Node":
                continue
            
            # Increment count for modality
            modality[self.planets[planet].quality] += 1

        # Iterate through modes, assign data to row
        for mode, count in modality.items():
            modes.append(mode)
            counts.append(str(count))

        # Create and return DataFrame
        df = pd.DataFrame({"Modality": modes, "Count": counts})
        return df
    
    def __build_aspects_data(self, subject: AstrologicalSubject) -> pd.DataFrame:
        """Build DataFrame object for the aspects table.

        Args:
            subject (AstrologicalSubject): Kerykeion object containing all calculations.

        Returns:
            pd.DataFrame: A pandas DataFrame object.
        """
        # Setup column lists
        p1: list = []
        asp: list = []
        p2: list = []
        
        # Setup aspect filter list
        aspects: list = ["conjunction", "opposition", "sextile", "square", "trine"]

        # Get aspects object
        nat = NatalAspects(user=subject)

        # Iterate through all aspects
        for aspect in nat.all_aspects:
            # Only use aspect types in filter list
            if aspect["aspect"] in aspects:
                
                # Filter and rename planet names for Planet 1
                p1name: str = ""
                if aspect["p1_name"] == "True_Node":
                    p1name = "N Node"
                elif aspect["p1_name"] in ChartUser.housename:
                    p1name = ChartUser.housename[aspect["p1_name"]]
                else:
                    p1name = aspect["p1_name"]

                # Filter and rename planet names for Planet 2
                p2name: str = ""
                if aspect["p2_name"] == "True_Node":
                    p2name = "N Node"
                elif aspect["p2_name"] in ChartUser.housename:
                    p2name = ChartUser.housename[aspect["p2_name"]]
                else:
                    p2name = aspect["p2_name"]

                # Assign data to row
                p1.append(p1name)
                asp.append(aspect["aspect"])
                p2.append(p2name)

            # Not in aspect filter list, skip
            else:
                continue

        # Create and return DataFrame
        df = pd.DataFrame({"Planet 1":p1,"Aspect":asp,"Planet 2":p2})
        return df
    
    def __build_table(self, table_type: Table) -> str:
        """Build a table given a Table object.

        Args:
            table_type (Table): A Table object under the TableType class, iterator at TableType.all

        Returns:
            str: A multi-line string formatted by PrettyTable.
        """
        # Create table object
        tbl: PrettyTable = PrettyTable()

        # Set field names from Table object
        tbl.field_names = table_type.columns

        # Create DataFrame from build_data dictionary
        df: pd.DataFrame = self.build_data[table_type]

        # Iterate through rows
        for _, data in df.iterrows():
            tbl.add_row(data)
        
        # Return table as string
        return tbl.get_string()
    
    def get_subject(self) -> AstrologicalSubject:
        """Gets an AstrologicalSubject object based on data from ChartUser.

        Returns:
            AstrologicalSubject: Kerykeion object containing all calculations.
        """
        return self.__make_subject()

    def get_chart_data(self, table_type: Table) -> pd.DataFrame:
        """Gets selected chart data.

        Args:
            table_type (Table): A table object under the TableType class, iterator at TableType.all

        Returns:
            pd.DataFrame: A pandas DataFrame object.
        """
        return self.build_data[table_type]
    
    def get_chart_as_str(self, table_type: Table) -> str:
        """Gets selected chart, a multi-line string formatted by PrettyTable.

        Args:
            table_type (Table): A table object under the TableType class, iterator at TableType.all

        Returns:
            str: A multi-line string formatted by PrettyTable.
        """
        return self.__build_table(table_type=table_type)
    
    def get_charts_as_str(self) -> dict[str, str]:
        """Get all charts as a string.

        Returns:
            list[str]: A list of string, each item will be a multi-line string formatted by PrettyTable.
        """
        tables: dict[str, str] = {}
        for table in Table:
            tables.update( {table.name.capitalize(): self.get_chart_as_str(table_type=table)} )
        return tables