import os
from datetime import datetime
from collections import Counter
from typing import Dict, Any
import requests


def get_daily_weather(location: str) -> Dict[str, Any]:
    """Return today's weather summary for a given location.

    Parameters
    ----------
    location:
        City name or "city,country" combination compatible with the
        OpenWeather API.

    Returns
    -------
    dict
        Dictionary containing today's temperature, general condition and
        chance of rain.
    """
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENWEATHER_API_KEY environment variable not set")

    params = {
        "q": location,
        "appid": api_key,
        "units": "metric",
    }
    response = requests.get(
        "https://api.openweathermap.org/data/2.5/forecast",
        params=params,
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()

    today = datetime.utcnow().date().isoformat()
    todays_entries = [
        entry for entry in data.get("list", [])
        if entry.get("dt_txt", "").startswith(today)
    ]
    if not todays_entries:
        todays_entries = data.get("list", [])[:1]

    temperatures = [entry["main"]["temp"] for entry in todays_entries]
    avg_temp = sum(temperatures) / len(temperatures)

    conditions = [entry["weather"][0]["description"] for entry in todays_entries]
    condition = Counter(conditions).most_common(1)[0][0]

    chance_of_rain = max((entry.get("pop", 0.0) for entry in todays_entries), default=0.0)

    return {
        "temperature": avg_temp,
        "condition": condition,
        "chance_of_rain": chance_of_rain,
    }
