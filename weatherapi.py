import asyncio
import json
from aiohttp import ClientSession


async def get_translation(text, source, target):
    async with ClientSession() as session:
        url = 'https://libretranslate.de/translate'
        data = {'q': text, 'source': source, 'target': target, 'format': 'text'}

        async with session.post(url, json=data) as response:
            translate_json = await response.json()

            try:
                return translate_json['translatedText']
            except KeyError:
                logger.error(f'Cannot get translation for word: {text}')
                return text

async def main():
	source = "ru"
	target = "en"
	city_ru = "саратов"

	cities = ['Moscow', 'St. Petersburg', 'Rostov-on-Don', 'Kaliningrad', 'Vladivostok',
          'Minsk', 'Beijing', 'Delhi', 'Istanbul', 'Tokyo', 'London', 'New York']
	res = []
	for i in cities:
		city_en = await get_translation(i, source, target)		
		res.append(city_en)
	print(res)

if __name__ == "__main__":
	asyncio.run(main())


