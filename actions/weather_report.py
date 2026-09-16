"""
actions/weather_report.py — Real-time weather reporting for Luna Assistant.
Fetches live temperature, weather condition, humidity, and wind using Open-Meteo API.
"""

from __future__ import annotations

import requests
from urllib.parse import quote_plus

# WMO Weather interpretation codes (WW)
_WMO_DESCRIPTIONS: dict[int, str] = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "foggy",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    56: "light freezing drizzle",
    57: "dense freezing drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    66: "light freezing rain",
    67: "heavy freezing rain",
    71: "slight snow fall",
    73: "moderate snow fall",
    75: "heavy snow fall",
    77: "snow grains",
    80: "slight rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    85: "slight snow showers",
    86: "heavy snow showers",
    95: "thunderstorm",
    96: "thunderstorm with slight hail",
    99: "thunderstorm with heavy hail",
}

def _fetch_weather(city: str) -> dict | None:
    """Fetch live weather data from Open-Meteo free API."""
    try:
        # Step 1: Geocode city name to lat/lon
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={quote_plus(city)}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url, timeout=6).json()
        results = geo_res.get("results")
        if not results:
            return None
        
        top = results[0]
        lat = top.get("latitude")
        lon = top.get("longitude")
        resolved_name = top.get("name", city)
        country = top.get("country", "")
        
        # Step 2: Fetch current weather metrics
        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
            f"&current=temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m"
        )
        w_res = requests.get(weather_url, timeout=6).json()
        current = w_res.get("current")
        if not current:
            return None
            
        code = current.get("weather_code", 0)
        condition = _WMO_DESCRIPTIONS.get(code, "clear")
        
        return {
            "city": resolved_name,
            "country": country,
            "temp_c": round(current.get("temperature_2m", 0.0), 1),
            "feels_like_c": round(current.get("apparent_temperature", 0.0), 1),
            "humidity": current.get("relative_humidity_2m", 0),
            "wind_kmh": round(current.get("wind_speed_10m", 0.0), 1),
            "condition": condition,
        }
    except Exception as e:
        print(f"[Weather] Live API fetch error: {e}")
        return None


def weather_action(
    parameters: dict,
    player=None,
    session_memory=None,
    speak=None,
) -> str:
    city = (parameters.get("city") or parameters.get("location") or "").strip()
    when = (parameters.get("time") or "today").strip()

    if not city:
        msg = "Which city would you like the weather for?"
        _log(msg, player)
        return msg

    # Try live weather fetch
    data = _fetch_weather(city)
    if data:
        place = f"{data['city']}, {data['country']}" if data['country'] else data['city']
        msg = (
            f"Right now in {place}, it's {data['temp_c']}°C ({data['condition']}), "
            f"feeling like {data['feels_like_c']}°C with {data['humidity']}% humidity and {data['wind_kmh']} km/h wind."
        )
    else:
        # Graceful fallback: Open browser search if geocoding fails
        import webbrowser
        search_query = f"weather in {city} {when}"
        url = f"https://www.google.com/search?q={quote_plus(search_query)}"
        try:
            webbrowser.open(url)
            msg = f"I've opened the weather report for {city} in your browser."
        except Exception as e:
            msg = f"I couldn't fetch the weather for {city} right now."

    _log(msg, player)

    if session_memory:
        try:
            session_memory.set_last_search(query=f"weather {city}", response=msg)
        except Exception:
            pass

    return msg


def _log(message: str, player=None) -> None:
    print(f"[Weather] {message}")
    if player:
        try:
            player.write_log(f"LUNA: {message}")
            if "°C" in message:
                player.show_content("WEATHER REPORT", message)
        except Exception:
            pass


# ── Tool declaration (auto-discovered by core/action_loader.py) ──────────────
TOOL = {
    "name": "weather_report",
    "description": "Gives the current live weather report for any city (temperature, conditions, humidity, wind).",
    "parameters": {
        "type": "OBJECT",
        "properties": {
            "city": {
                "type": "STRING",
                "description": "City name (e.g. Tokyo, New York, London, Paris)"
            },
            "time": {
                "type": "STRING",
                "description": "today | tomorrow | weekend (optional)"
            }
        },
        "required": [
            "city"
        ]
    },
    "handler": weather_action,
}

weather_report = weather_action
