# External
import json, logging
from enum import Enum


class DataSource(Enum):
    """Enum for possible data sources.
    """
    json = "JSON data"

    @property
    def full(self) -> str:
        return self.value

class Data:
    '''Class for accessing and manipulating data'''
    def __init__(self, file: str, source: DataSource) -> None:
        '''Class for accessing and manipulating data
        :file: File path for data source
        :source: Data source object. Data.Source.Type object, enumated in Data.Source.sources'''
        self.path: str                  = file
        self.source: DataSource         = source

    def __load_data(self) -> dict:
        '''Wraps buffering of data from any source. Returns dict'''
        match self.source:
            case DataSource.json:
                return self.__load_json()
            case _: return {} # This should never happen. Update loop with new data sources.

    def __load_json(self) -> dict:
        '''Buffers json from self.path. Returns dict'''
        try:
            logging.info(f"Loading data from file: {self.path}")
            with open(file=self.path, mode="r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"*** File load error: {str(e)}")
            logging.warning(f"Assuming file is empty or missing, returning empty dataset.")
            return {}

    def __write_json(self, data: dict) -> None:
        '''Writes json to self.path from self.data'''
        try:
            logging.info(f"Writing data to file: {self.path}")
            with open(file=self.path, mode='w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"*** File write error: {str(e)}")

    def load_data(self) -> dict:
        '''Load from data source to buffer. Returns dict'''
        return self.__load_data()

    def write_data(self, data: dict) -> None:
        '''Write buffer to data source'''
        match self.source:
            case DataSource.json: 
                self.__write_json(data=data)
            case _: 
                return # This should never happen. Update loop with new data sources.