import asyncio # to get able async
import json # convert objects to json
from aiohttp import ClientSession # request web pages
import urllib.parse # join urls
from bs4 import BeautifulSoup # parse html


class Input:
    """
    Getting input from user
    """

    STDIN = "stdin"

    def __init__(self, inmethod="stdin"):
        """
        Defining method of fetching data.
        This is convenient because we can fast change method of fetching data.
        Like from requesting HTTP or sockets or simple stdin.
        """
        self.STDIN = "stdin"
        self.HTTP = "http"

        self.inmethod = inmethod

    def get_city(self):
        result = None
        if self.inmethod == self.STDIN:
            result = self.__get_stdin__()
        elif self.inmethod == self.HTTP:
            result = self.__get_http__()
        return result

    def __get_stdin__(self):
        result = input("City? ")
        return result

    def __get_http__(self):
        """
        For exmaple, listen HTTP GET requests.
        Fetch city from parametrs(?city=Казань) or path (http://weather.com/калининград).
        """
        pass
    

class TranslatorAPI:
    """
    Translator API from ru to en
    """
    def __init__(self):
        self.url = 'https://libretranslate.de/translate'

    async def get_trans(self, text, source="ru", target="en"):
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
    def __init__(self):
        self.service_url = 'https://yandex.ru/pogoda/'
    
    async def get_content(self, city):
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
    
    async def parse(self, soup):
        forecast = soup.find("div", class_="forecast-briefly__days")
        forecast_10days = forecast.find_all("li", class_="forecast-briefly__day")
        for each_day in forecast_10days:
            print(each_day)

    async def get(self, city):
        #soup = await self.get_content(city)
        soup = BeautifulSoup(open("doc.html"), "html.parser")
        weather = await self.parse(soup)
        return weather

class DAOManager:
    """
    Data Access Object Manager for DBMS
    """
    pass


async def main():
    try:
        _input = Input()
        _translator = TranslatorAPI()
        _weather = WeatherScrapper()
        """
        _db = DAOManager()
        """

        #city_ru = _input.get_city()
        #city_en = await _translator.get_trans(city_ru)
        city_en = "kaliningrad"
        city_weather = await _weather.get(city_en)
        """
        _db.save(city_weather)
        """
        #print(city_weather)
    except Exception as error:
        print(f"Error {error}")


if __name__ == "__main__":
    asyncio.run(main())

