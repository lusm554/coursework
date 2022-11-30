import asyncio
import json
from aiohttp import ClientSession

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
                except KeyError:
                    print(f"Error in TranslatorAPI.get_trans with text: {text}")
                    return text

class WeatherScrapper:
    """
    Weather API scapper
    """
    pass


class DAOManager:
    """
    Data Access Object Manager for DBMS
    """
    pass


async def main():
    _input = Input()
    _translator = TranslatorAPI()
    """
    _weather = WeatherScrapper()
    _db = DAOManager()
    """

    city_en = _input.get_city()
    city_ru = await _translator.get_trans(city_en)
    """
    city_weather = _weather.get(city_en)
    _db.save(city_weather)
    """
    print(city_en)
    print(city_ru)

if __name__ == "__main__":
    asyncio.run(main())
