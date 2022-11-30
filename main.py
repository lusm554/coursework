class Input:
    """
    Getting input from user
    """
    pass

class TranslatorAPI:
    """
    Translator API from ru to en
    """
    pass

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



def main():
    _input = Input()
    _translator = TranslatorAPI()
    _weather = WeatherScrapper()
    _db = DAOManager()

    city_en = _input.get_city()
    city_ru = _translator.en2ru(city_en)
    city_weather = _weather.get(city_en)
    _db.save(city_weather)

if __name__ == "__main__":
    main()
