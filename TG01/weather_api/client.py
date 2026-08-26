import logging
import ssl

import aiohttp
import certifi
from django.conf import settings
from pydantic import AliasChoices, BaseModel, Field

logger = logging.getLogger(__name__)

_weather_session: aiohttp.ClientSession | None = None

class WeatherMain(BaseModel):
    temp: float
    feels_like: float = Field(
        validation_alias = AliasChoices('feels_like', 'feelsLike', 'FeelsLike'), 
    )    

class WeatherCondition(BaseModel):
    description: str

class OpenWeatherResponse(BaseModel):
    main: WeatherMain
    weather: list[WeatherCondition]

async def get_weather_by_city(city_name: str) -> dict | None:
    api_key = settings.WEATHER.api_key
    api_url = settings.WEATHER.api_url

    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric",
        "lang": "ru",
    }

    session = await _get_weather_session()

    try:
        async with session.get(api_url, params=params, timeout=10) as response:
            if response.status == 200:
                raw_data = await response.json()
                # print(raw_data)
                data = OpenWeatherResponse(**raw_data)

                return {
                    "temp": round(data.main.temp),
                    "feels_like": round(data.main.feels_like),
                    "description": data.weather[0].description
                }
            elif response.status == 404:
                return None
            else:
                logger.error(f"Ошибка API погоды: HTTP {response.status}")
                return None
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка сети при погоды: {e}")
        return None        

async def _get_weather_session() -> aiohttp.ClientSession: 
    global _weather_session   

    if _weather_session is None or _weather_session.closed:
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        _weather_session = aiohttp.ClientSession(connector=connector)

    return _weather_session

async def close_weather_session():

    if _weather_session is not None and not _weather_session.closed:
        await _weather_session.close()
        logger.info("HTTP-сессия с OpenWeather успешно закрыта.")