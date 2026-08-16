import time
import httpx
from pydantic import BaseModel


class CurrentWeather(BaseModel):
    temperature_2m: float


class WeatherResponse(BaseModel):
    latitude: float
    longitude: float
    current: CurrentWeather


def get_weather():
    url = "https://api.open-meteo.com/v1/forecast?latitude=13.08&longitude=80.27&current=temperature_2m"

    for attempt in range(5):
        try:
            response = httpx.get(url, timeout=10.0)
            return response  # success -> stop retrying
        except (httpx.TimeoutException, httpx.ConnectError) as e:
            wait = 2 ** attempt
            print(f"attempt {attempt + 1} failed ({e}), retrying in {wait}s")
            time.sleep(wait)

    raise Exception("All retries failed")


response = get_weather()
print(response.status_code)

weather_response = WeatherResponse(**response.json())
print(weather_response.latitude)
print(weather_response.longitude)
print(weather_response.current.temperature_2m)