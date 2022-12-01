import asyncio # to get able async
import json # convert objects to json
from aiohttp import ClientSession # request web pages
import urllib.parse # join urls
from bs4 import BeautifulSoup # parse html
import sqlite3 # db api 
from datetime import datetime # set ctl timestamps
from prettytable import from_db_cursor as table_from_cursor # print tables


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
        result = input("City? ").lower()
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

class WeatherScraper:
    """
    Weather API scapper
    """
    def __init__(self) -> None:
        self.service_url = 'https://yandex.ru/pogoda/'
    
    async def get_content(self, city: str) -> str:
        city = city.strip().replace(" ", "-")
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
        try:
            clean_forecast = []
            forecast = soup.find("div", class_="forecast-briefly__days")
            forecast_month = forecast.find_all("li", class_="forecast-briefly__day")
            for each_day in forecast_month:
                sdweather = each_day.find("a")["aria-label"]
                keys = ["weekday", "month", "weather", "temperature_day", "temperature_night"]
                objdweather = dict(zip(keys, sdweather.split(", ")))
                objdweather["raw_weather"] = sdweather
                clean_forecast.append(objdweather)
            return clean_forecast
        except Exception as error:
            raise ValueError("Error at WeatherScraper.__parse__: Network error. Yandex thinks it's robot.")

    def __db_format__(self, weather: [{}], city: str) -> [()]:
        """
        Set hard order of fields for writing to bd. 
        """
        # я а 
        nmonth = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря']
        formatted_weather = []
        ordered_schema = ("city", "report_date", "weather", "temperature_day", "temperature_night", "raw_weather")
        for each_obj in weather:
            day, month = each_obj["month"].split(" ")
            report_date = datetime.strptime(f"{day}-{nmonth.index(month)+1}-{datetime.now().year}", "%d-%m-%Y") # TODO: fix problems with current year
            dobj = {
                "city": city.lower(),
                "report_date": str(report_date),
            }
            dobj = {**each_obj, **dobj}
            t = tuple([dobj[key] for key in ordered_schema])
            formatted_weather.append(t)
        return formatted_weather

    async def get(self, city: str) -> [()]:
        try:
            soup = await self.get_content(city)
            # soup = BeautifulSoup(open("doc.html"), "html.parser") # mock data
            weather = await self.__parse__(soup)
            formatted_weather = self.__db_format__(weather, city)
            return formatted_weather
        except Exception as error:
            raise error


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
            city TEXT,
            report_date TEXT,
            weather TEXT,
            temperature_day TEXT,
            temperature_night TEXT,
            raw_weather TEXT,
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
        CTL_DATE = str(datetime.timestamp(datetime.now())) # get current timestamp, like 1594819641.9622827
        CTL_ACTION = "I" # by now only I(insert)

        data_wctl = []
        # add ctl fields
        for each_obj in data:
            data_wctl.append((*each_obj, CTL_ID, CTL_DATE, CTL_ACTION))

        insert = """ 
        INSERT INTO weather(
            city,
            report_date,
            weather,
            temperature_day,
            temperature_night,
            raw_weather,
            ctl_id,
            ctl_date,
            ctl_action
        ) 
        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cur.executemany(insert, data_wctl)
        self.conn.commit()

    def get(self, sql: str, args: list=[], is_extracted_data=True):
        cur = self.conn.cursor()
        data = cur.execute(sql, args)
        if is_extracted_data:
            data = data.fetchall()
        return data 


class WeatherServiceAPI():
    """
    Contain methods of this service.
    Methods:
        - Get Day Weather. If weather not in database or out of date, then request some and save it.
        - Get All Weather. Just show user weather we have.
        - Get average temp in month by city.
    """
    def __init__(self, db: str="test.db"):
        self._input = Input()
        self._translator = TranslatorAPI() # TODO: change transator to transcriptor
        self._weather_scraper = WeatherScraper()
        self._db = DAOManager(db=db)
    
    async def __is_weather_exist__(self, city: str) -> bool:
        """
        Check is weather exist and not out of date.
        NOT THE BEST SOLUTION. SEARCH TIME DEPENDS OF COUNT OF WEATHER.
        """
        select = "SELECT * FROM weather where city = ?"
        weather_by_city = self._db.get(select, (city.lower(),))
        today = datetime.today().strftime("%Y-%m-%d") # af date format
        weather_exist = len(weather_by_city) != 0
        weather_not_outofdate = any((today in dweather[2]) for dweather in weather_by_city)
        if weather_exist and weather_not_outofdate:
            return True
        return False

    def scrape_ifnexist_decorator(func2decorate):
        async def wrap(*args):
            # scrap here
            city_ru = args[1]
            self = args[0]
            #city_en = await self._translator.get_trans(city_ru)
            city_en = city_ru
            if not await self.__is_weather_exist__(city_en):
                print("weather not exist")
                city_weather = await self._weather_scraper.get(city_en)
                self._db.set(city_weather)
            else:
                print("weather exist")
            await func2decorate(*args)
        return wrap

    @scrape_ifnexist_decorator
    async def get_month_weather(self, city: str):
        month_w = """
        SELECT
            forecast_id, city, report_date, weather, temperature_day, temperature_night
        FROM weather
        WHERE city = ?
        """
        data = self._db.get(month_w, (city,), is_extracted_data=False)
        table = table_from_cursor(data)
        print(table)

    @scrape_ifnexist_decorator
    async def get_avg_weather(self, city: str):
        avg_w = """
        SELECT
            AVG(
                CAST(SUBSTR(temperature_day, INSTR(temperature_day, ' ')+1, INSTR(temperature_day, '°')-(INSTR(temperature_day, ' ')+1)) as DECIMAL)
            ) as avg_day,
            AVG(
                CAST(SUBSTR(temperature_night, INSTR(temperature_night, ' ')+1, INSTR(temperature_night, '°')-(INSTR(temperature_night, ' ')+1)) as DECIMAL)
            ) as avg_night
        FROM weather
        WHERE city = ?
        """
        data = self._db.get(avg_w, (city,), is_extracted_data=False)
        table = table_from_cursor(data)
        print(table)
    
    @scrape_ifnexist_decorator
    async def get_available_cities(self, city: str):
        available_w = """ 
        SELECT DISTINCT city
        from weather 
        """
        data = self._db.get(available_w, is_extracted_data=False)
        table = table_from_cursor(data)
        print(table)

    async def run(self):
        try:
            def print_menu() -> None:
                print("Select number: ")
                for n, key in enumerate(commands.keys()):
                    print(f"{n+1}. {key[1].capitalize()}")
                print()

            commands = {
                (1, "exit"): lambda: exit(0),
                (2, "month_weather"): self.get_month_weather,
                (3, "avg_weather"): self.get_avg_weather,
                (4, "available_cities"): self.get_available_cities,
            }

            while 1:
                try:
                    print_menu()
                    cmd = input("Which one? ")
                    city = None
                    method = None # TODO: final methods
                    cmd = int(cmd)
                    
                    for fname, f in commands.items():
                        if cmd in fname:
                            if cmd == 1:
                                f()
                            else:
                                method = f
                            break
                    else:
                        print("Command not found", "\n")
                        continue

                    city = self._input.get_city() 
                    await method(city)
                    print()
                except Exception as error:
                    if "invalid literal for int()" in str(error):
                        print("Not a number.")
                    else:
                        print(error)
                    print()
        except Exception as error:
            print(error)


async def main():
    weather_service = WeatherServiceAPI(db="test.db")
    await weather_service.run()

if __name__ == "__main__":
    asyncio.run(main())

