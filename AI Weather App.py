"""
AI Weather App — Python Edition
================================
Features:
  - Location-based weather (city name or GPS coords)
  - Current conditions + 5-day forecast
  - AI recommendations via Anthropic Claude API

Dependencies:
  pip install requests anthropic python-dotenv

Usage:
  python ai_weather_app.py
  python ai_weather_app.py --city "Mumbai"
  python ai_weather_app.py --lat 19.07 --lon 72.87
  python ai_weather_app.py --city "Tokyo" --no-ai

Add your Anthropic API key either:
  - In a .env file:  ANTHROPIC_API_KEY=sk-ant-...
  - Or as env var:   export ANTHROPIC_API_KEY=sk-ant-...
"""

import argparse
import os
import sys
from datetime import datetime, timedelta
from typing import Optional

import requests
from dotenv import load_dotenv

# ─── Optional: Anthropic SDK ────────────────────────────────────────────────
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

load_dotenv()

# ─── Constants ───────────────────────────────────────────────────────────────

GEOCODE_URL   = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL   = "https://api.open-meteo.com/v1/forecast"
REVERSE_GEO   = "https://geocoding-api.open-meteo.com/v1/reverse"

WMO_DESCRIPTIONS = {
    0:  ("Clear sky",        "☀️"),
    1:  ("Mainly clear",     "🌤️"),
    2:  ("Partly cloudy",    "⛅"),
    3:  ("Overcast",         "☁️"),
    45: ("Foggy",            "🌫️"),
    48: ("Icy fog",          "🌫️"),
    51: ("Light drizzle",    "🌦️"),
    53: ("Drizzle",          "🌦️"),
    55: ("Heavy drizzle",    "🌦️"),
    61: ("Light rain",       "🌧️"),
    63: ("Rain",             "🌧️"),
    65: ("Heavy rain",       "🌧️"),
    71: ("Light snow",       "🌨️"),
    73: ("Snow",             "❄️"),
    75: ("Heavy snow",       "❄️"),
    80: ("Rain showers",     "🌦️"),
    81: ("Heavy showers",    "🌧️"),
    82: ("Violent showers",  "⛈️"),
    95: ("Thunderstorm",     "⛈️"),
    96: ("Hail storm",       "⛈️"),
    99: ("Heavy hail storm", "⛈️"),
}


# ─── Data Classes ─────────────────────────────────────────────────────────────

class CurrentWeather:
    def __init__(self, data: dict):
        c = data["current"]
        self.temperature     = round(c["temperature_2m"], 1)
        self.feels_like      = round(c["apparent_temperature"], 1)
        self.humidity        = round(c["relative_humidity_2m"])
        self.wind_speed      = round(c["wind_speed_10m"], 1)
        self.weather_code    = c["weather_code"]
        desc, icon           = WMO_DESCRIPTIONS.get(self.weather_code, ("Unknown", "🌡️"))
        self.description     = desc
        self.icon            = icon

    def __str__(self):
        return (
            f"{self.icon}  {self.description}\n"
            f"   Temperature : {self.temperature}°C  (feels like {self.feels_like}°C)\n"
            f"   Humidity    : {self.humidity}%\n"
            f"   Wind        : {self.wind_speed} km/h"
        )


class DailyForecast:
    def __init__(self, date_str: str, code: int, temp_max: float, temp_min: float):
        self.date        = datetime.strptime(date_str, "%Y-%m-%d")
        self.weather_code = code
        self.temp_max    = round(temp_max, 1)
        self.temp_min    = round(temp_min, 1)
        desc, icon       = WMO_DESCRIPTIONS.get(code, ("Unknown", "🌡️"))
        self.description = desc
        self.icon        = icon

    @property
    def day_name(self) -> str:
        today = datetime.today().date()
        if self.date.date() == today:
            return "Today    "
        elif self.date.date() == today + timedelta(days=1):
            return "Tomorrow "
        return self.date.strftime("%A   ")

    def __str__(self):
        return (
            f"  {self.day_name}  {self.icon}  {self.description:<18}"
            f"  ↑ {self.temp_max}°C  ↓ {self.temp_min}°C"
        )


class WeatherReport:
    def __init__(self, city: str, current: CurrentWeather, forecast: list[DailyForecast]):
        self.city     = city
        self.current  = current
        self.forecast = forecast
        self.ai_recommendation: Optional[str] = None


# ─── Core Functions ──────────────────────────────────────────────────────────

def geocode_city(city: str) -> tuple[float, float, str]:
    """Convert a city name to (lat, lon, display_name)."""
    resp = requests.get(GEOCODE_URL, params={"name": city, "count": 1, "language": "en", "format": "json"}, timeout=10)
    resp.raise_for_status()
    results = resp.json().get("results")
    if not results:
        raise ValueError(f"City '{city}' not found. Try a different spelling.")
    r = results[0]
    display = f"{r['name']}, {r.get('admin1', '')}, {r.get('country', '')}".strip(", ")
    return r["latitude"], r["longitude"], display


def reverse_geocode(lat: float, lon: float) -> str:
    """Convert coordinates to a city name."""
    try:
        resp = requests.get(REVERSE_GEO, params={"latitude": lat, "longitude": lon, "language": "en", "format": "json"}, timeout=10)
        resp.raise_for_status()
        d = resp.json()
        return f"{d.get('name', '')}, {d.get('country', '')}".strip(", ")
    except Exception:
        return f"{lat:.2f}, {lon:.2f}"


def fetch_weather(lat: float, lon: float) -> dict:
    """Fetch current + 5-day forecast from Open-Meteo."""
    params = {
        "latitude":  lat,
        "longitude": lon,
        "current":   "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
        "daily":     "weather_code,temperature_2m_max,temperature_2m_min",
        "timezone":  "auto",
        "forecast_days": 5,
    }
    resp = requests.get(WEATHER_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def build_report(data: dict, city: str) -> WeatherReport:
    """Parse raw API response into a WeatherReport."""
    current  = CurrentWeather(data)
    daily    = data["daily"]
    forecast = [
        DailyForecast(
            daily["time"][i],
            daily["weather_code"][i],
            daily["temperature_2m_max"][i],
            daily["temperature_2m_min"][i],
        )
        for i in range(len(daily["time"]))
    ]
    return WeatherReport(city=city, current=current, forecast=forecast)


def get_ai_recommendation(report: WeatherReport, api_key: str) -> str:
    """Call Claude to generate a personalised weather recommendation."""
    if not ANTHROPIC_AVAILABLE:
        raise ImportError("Run: pip install anthropic")

    c = report.current
    forecasts_summary = ", ".join(
        f"{d.day_name.strip()}: {d.temp_max}°C/{d.temp_min}°C {d.description}"
        for d in report.forecast[:3]
    )

    prompt = (
        f"Weather in {report.city}:\n"
        f"Current: {c.description}, {c.temperature}°C, feels like {c.feels_like}°C, "
        f"humidity {c.humidity}%, wind {c.wind_speed} km/h.\n"
        f"3-day forecast: {forecasts_summary}\n\n"
        "Give a friendly, practical 2-3 sentence recommendation: "
        "what to wear, umbrella needed, best time to go outside, or activity ideas. "
        "Be specific and conversational. Plain text only, no markdown."
    )

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


# ─── Display ─────────────────────────────────────────────────────────────────

def print_report(report: WeatherReport):
    width = 56
    print("\n" + "═" * width)
    print(f"  🌍  {report.city}")
    print("─" * width)
    print("🔥 LIVE AI WEATHER REPORT")
    if report.current.temperature > 35:
     print("  🔥 Too hot today! Stay hydrated.")
    print("  Have a nice day 😄")
    print("\n" + "─" * width)
    print("\n  5-DAY FORECAST\n")
    for day in report.forecast:
        print(f"  {day}")
    if report.ai_recommendation:
        print("\n" + "─" * width)
        print("\n  🤖  AI RECOMMENDATION\n")
        # Word-wrap to ~52 chars
        words = report.ai_recommendation.split()
        line = "  "
        for word in words:
            if len(line) + len(word) + 1 > 54:
                print(line)
                line = "  " + word + " "
            else:
                line += word + " "
        if line.strip():
            print(line)
    print("\n" + "═" * width + "\n")


# ─── CLI Entry Point ──────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="AI Weather App")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--city", type=str, help="City name, e.g. 'Mumbai'")
    group.add_argument("--lat",  type=float, help="Latitude (use with --lon)")
    parser.add_argument("--lon",   type=float, help="Longitude (use with --lat)")
    parser.add_argument("--no-ai", action="store_true", help="Skip AI recommendation")
    args = parser.parse_args()

    # ── 1. Resolve location ──────────────────────────────────────────────────
    if args.city:
        print(f"\n🔍  Locating '{args.city}'...")
        lat, lon, city = geocode_city(args.city)
    elif args.lat and args.lon:
        lat, lon = args.lat, args.lon
        city = reverse_geocode(lat, lon)
        print(f"\n📍  Resolved to: {city}")
    else:
        # Interactive prompt when no args provided
        city_input = input("\nEnter city name (or press Enter to use coordinates): ").strip()
        if city_input:
            print(f"🔍  Locating '{city_input}'...")
            lat, lon, city = geocode_city(city_input)
        else:
            lat  = float(input("Latitude : "))
            lon  = float(input("Longitude: "))
            city = reverse_geocode(lat, lon)

    # ── 2. Fetch weather ─────────────────────────────────────────────────────
    print(f"⛅  Fetching weather for {city}...")
    raw_data = fetch_weather(lat, lon)
    report   = build_report(raw_data, city)

    # ── 3. AI recommendation ─────────────────────────────────────────────────
    if not args.no_ai:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("⚠️   No ANTHROPIC_API_KEY found — skipping AI recommendation.")
            print("    Add it to a .env file or export it as an environment variable.\n")
        elif not ANTHROPIC_AVAILABLE:
            print("⚠️   anthropic package not installed — run: pip install anthropic\n")
        else:
            print("🤖  Asking Claude for recommendations...")
            try:
                report.ai_recommendation = get_ai_recommendation(report, api_key)
            except Exception as e:
                print(f"⚠️   AI recommendation failed: {e}\n")

    # ── 4. Print report ──────────────────────────────────────────────────────
    print_report(report)
# ─── Extension hooks — add your own features here ────────────────────────────
#
# Examples to build on top of this file:
#
#   1. Save to JSON / CSV
#      with open("weather_log.json", "a") as f:
#          import json; json.dump({"city": report.city, "temp": report.current.temperature, ...}, f)
#
#   2. Send weather to your phone via Twilio SMS
#      from twilio.rest import Client
#      client = Client(account_sid, auth_token)
#      client.messages.create(to="+1234567890", from_="+0987654321", body=str(report.current))
#
#   3. Add a Flask web server
#      from flask import Flask, jsonify
#      app = Flask(__name__)
#      @app.route("/weather/<city>")
#      def weather(city): ...
#
#   4. Hourly weather breakdown
#      Add "hourly=temperature_2m,precipitation_probability" to fetch_weather() params
#      and parse data["hourly"] the same way as daily.
#
#   5. Weather alerts
#      if report.current.weather_code >= 80:
#          send_alert("Severe weather detected!")
#
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBye! 👋\n")
    except Exception as e:
        print(f"\n❌  Error: {e}\n")
        sys.exit(1)