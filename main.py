import asyncio # to get able async
import json # convert objects to json
from aiohttp import ClientSession # request web pages
import urllib.parse # join urls
from bs4 import BeautifulSoup # parse html
import sqlite3 # db api 
import time # set ctl timestamps


class Input:
    """
    Getting input from user
    """
    def __init__(self, inmethod: str="stdin") -> None:
        """
        Defining method of fetching data.
        This is convenient because we can fast change method of fetching data.
        Like from requesting HTTP or sockets or simple stdin.
        """
        self.STDIN = "stdin"
        self.HTTP = "http"

        self.inmethod = inmethod

    def get_city(self) -> str:
        result = None
        if self.inmethod == self.STDIN:
            result = self.__get_stdin__()
        elif self.inmethod == self.HTTP:
            result = self.__get_http__()
        return result

    def __get_stdin__(self) -> str:
        result = input("City? ")
        return result

    def __get_http__(self) -> None:
        """
        For exmaple, listen HTTP GET requests.
        Fetch city from parametrs(?city=Казань) or path (http://weather.com/калининград).
        """
        pass
    

class TranslatorAPI:
    """
    Translator API from ru to en
    """
    def __init__(self) -> None:
        self.url = 'https://libretranslate.de/translate'

    async def get_trans(self, text: str, source: str="ru", target: str="en") -> str:
        async with ClientSession() as session:
            data = {'q': text, 'source': source, 'target': target, 'format': 'text'}
            async with session.post(self.url, json=data) as response:
                trans_json = await response.json()
                try:
                    return trans_json['translatedText']
                except KeyError as error:
                    print(f"Error in TranslatorAPI.get_trans with text: {text}")
                    raise error

class WeatherScrapper:
    """
    Weather API scapper
    """
    def __init__(self) -> None:
        self.service_url = 'https://yandex.ru/pogoda/'
    
    async def get_content(self, city: str) -> str:
        print("WeatherScrapper.get city", city)
        async with ClientSession() as session:
            city_weather_url = urllib.parse.urljoin(self.service_url, city)
            print("WeatherScrapper.get url", city_weather_url)
            async with session.get(city_weather_url) as response:
                try:
                    html = await response.text()
                    return BeautifulSoup(html, "html.parser")
                except Exception as error:
                    print(f"Error in WeatherScrapper.get: {error}")
                    raise error
    
    async def __parse__(self, soup: BeautifulSoup) -> [{}]:
        clean_forecast = []
        forecast = soup.find("div", class_="forecast-briefly__days")
        forecast_month = forecast.find_all("li", class_="forecast-briefly__day")
        for each_day in forecast_month:
            sdweather = each_day.find("a")["aria-label"]
            keys = ["weekday", "month", "weather", "temperature_day", "temperature_night"]
            objdweather = dict(zip(keys, sdweather.split(", ")))
            clean_forecast.append(objdweather)
        return clean_forecast

    def __db_format__(self, weather: [{}]) -> [()]:
        """
        Set hard order of fields for writing to bd. 
        """
        formatted_weather = []
        ordered_schema = ("weekday", "month", "weather", "temperature_day", "temperature_night")
        for each_obj in weather:
            t = [each_obj[key] for key in ordered_schema]
            formatted_weather.append(t)
        return formatted_weather

    async def get(self, city: str) -> [()]:
        #soup = await self.get_content(city)
        soup = BeautifulSoup(open("doc.html"), "html.parser") # mock data
        weather = await self.__parse__(soup)
        formatted_weather = self.__db_format__(weather)
        return formatted_weather

class DAOManager:
    """
    Data Access Object Manager for DBMS
    """
    def __init__(self, db: str="test.db") -> None:
        self.conn = sqlite3.connect(db)
        self.__setup_db__()
    
    def __setup_db__(self) -> None:
        """
        Set up default DB tables.
        clt_id      - ИД загрузки
        clt_date    - дата загрузки
        clt_action  - действие, U - update, I - insert
        """
        cur = self.conn.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS weather (
            forecast_id INTEGER PRIMARY KEY AUTOINCREMENT,
            weekday TEXT,
            month TEXT,
            weather TEXT,
            temperature_day TEXT,
            temperature_night TEXT,
            ctl_id INTEGER,
            ctl_date TEXT,
            ctl_action TEXT
        )
        """
        cur.execute(create_table_query)
    
    def __get_last_ctl_load__(self, cur: sqlite3.Cursor) -> int:
        select_max_ctl_id = """
        SELECT 
            CASE
                WHEN MAX(ctl_id) IS NULL THEN 0 -- in case when rows does not exist
                ELSE MAX(ctl_id)
            END AS max_ctl_id
        FROM weather
        """
        res = cur.execute(select_max_ctl_id).fetchone()[0]
        return res

    def set(self, data: [(str, str, str, str, str)]) -> None: 
        cur = self.conn.cursor()
        CTL_ID = self.__get_last_ctl_load__(cur)+1 # load id
        CTL_DATE = str(time.time()) # get current timestamp, like 1594819641.9622827
        CTL_ACTION = "I" # by now only I(insert)

        data_wctl = []
        # add ctl fields
        for each_obj in data:
            data_wctl.append((*each_obj, CTL_ID, CTL_DATE, CTL_ACTION))

        insert = """ 
        INSERT INTO weather(
            weekday,
            month,
            weather,
            temperature_day,
            temperature_night,
            ctl_id,
            ctl_date,
            ctl_action
        ) 
        VALUES(?, ?, ?, ?, ?, ?, ?, ?)
        """
        cur.executemany(insert, data_wctl)
        self.conn.commit()

    def get(self, data=None):
        cur = self.conn.cursor()
        select = """
        SELECT *
        FROM weather
        """
        data_iter = cur.execute(select)
        return data_iter

class ServiceAPI():
    """
    Contain methods of this service.
    Methods:
        - Get Day Weather. If weather not in database or out of date, then request some and save it.
        - Get All Weather. Just show user weather we have.
        - Get average temp in month by city.
    """
    pass

async def main():
    try:
        _input = Input()
        _translator = TranslatorAPI()
        _weather = WeatherScrapper()
        _db = DAOManager()

        city_ru = _input.get_city()
        city_en = await _translator.get_trans(city_ru)
        # city_en = "kaliningrad" # mock data
        city_weather = await _weather.get(city_en)
        _db.set(city_weather)
        for i in _db.get():
            print(i)
    except Exception as error:
        print(f"Error {error}")
        raise error


if __name__ == "__main__":
    asyncio.run(main())

