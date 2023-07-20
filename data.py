# External
import json, logging

class Data:
    '''Class for accessing and manipulating data'''
    class Source:
        '''Container class for data sources. Use 'types' for iteration.'''
        class Type:
            '''Container class for individual data sources'''
            def __init__(self, name: str, full: str) -> None:
                self.name: str = name
                self.full: str = full
        json: Type = Type(name="json", full="json data")
        types: dict[str, Type] = {"json": json}

    def __init__(self, file: str, source: Source.Type) -> None:
        '''Class for accessing and manipulating data
        :file: File path for data source
        :source: Data source object. Data.Source.Type object, enumated in Data.Source.sources'''
        self.path: str = file
        self.source: Data.Source.Type = source
        self.data: dict = {}
        self.__load_data()

    def __load_data(self) -> None:
        '''Wraps buffering of data from any source into self.data'''
        match self.source:
            case Data.Source.json:
                self.__load_json()
            case _: pass # This should never happen. Update loop with new data sources.

    def __load_json(self) -> None:
        '''Buffers json from self.path into self.data'''
        try:
            logging.info(f"Loading data from file: {self.path}")
            with open(file=self.path, mode="r", encoding="utf-8") as f:
                self.data = json.load(f)
            return
        except Exception as e:
            logging.error(f"*** File load error: {str(e)}")
            logging.warning(f"Assuming file is empty or missing, returning empty dataset.")
            return

    def __write_json(self) -> None:
        '''Writes json to self.path from self.data'''
        try:
            logging.info(f"Writing data to file: {self.path}")
            with open(file=self.path, mode='w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"*** File write error: {str(e)}")

    def load_data(self) -> None:
        '''Load from data source to buffer'''
        self.__load_data()

    def write_data(self) -> None:
        '''Write buffer to data source'''
        match self.source:
            case Data.Source.json: self.__write_json()
            case _: return # This should never happen. Update loop with new data sources.