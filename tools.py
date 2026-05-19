"""
LangChain tools for the travel_agent project.

This module exposes five tools using the `@tool` decorator from
`langchain.tools`:

- `search_flights(source, destination)`
- `search_hotels(city, max_price_per_night)`
- `search_places(city)`
- `get_weather(city, travel_date)`
- `estimate_budget(flight_price, hotel_price_per_night, num_days)`

All file reads and network calls use try/except and return human-readable
error strings on failure.
"""

import json
import os
from datetime import datetime
from typing import Any

import requests
from langchain.tools import tool


def _data_path(filename: str) -> str:
	return os.path.join(os.path.dirname(__file__), "data", filename)


@tool
def search_flights(query: str) -> str:
	"""Search for flights. Input format: 'source,destination' e.g. 'Delhi,Goa'"""
	parts = query.split(",")
	source = parts[0].strip().title()
	destination = parts[1].strip().title()
	try:
		path = _data_path("flights.json")
		with open(path, "r", encoding="utf-8") as f:
			flights = json.load(f)
	except Exception as e:
		return f"Error reading flights data: {e}"

	matches = [
		fl for fl in flights
		if str(fl.get("source", "")).strip().title() == source
		and str(fl.get("destination", "")).strip().title() == destination
	]

	if not matches:
		return f"No flights found from {source} to {destination}."

	cheapest = min(matches, key=lambda x: float(x.get("price_inr", float('inf'))))
	return (
		f"Cheapest flight {cheapest.get('flight_id')} — {cheapest.get('airline')}: "
		f"{cheapest.get('source')} → {cheapest.get('destination')}, "
		f"Dep {cheapest.get('departure_time')}, Arr {cheapest.get('arrival_time')}, "
		f"Price: ₹{cheapest.get('price_inr')}, Duration: {cheapest.get('duration_hours')}h, "
		f"Class: {cheapest.get('class')}"
	)


@tool
def search_hotels(query: str) -> str:
	"""Search for hotels. Input format: 'city,max_price,preference' e.g. 'Goa,5000,budget'
	preference: budget/luxury/family/couple/solo (optional, default: all)"""
	parts = query.split(",")
	city = parts[0].strip().title()
	max_price = int(parts[1].strip()) if len(parts) > 1 else 10000
	preference = parts[2].strip().lower() if len(parts) > 2 else None

	# Map preferences to hotel types
	preference_map = {
		"budget": "budget",
		"luxury": "luxury",
		"family": "standard",
		"couple": "luxury",
		"solo": "budget",
	}

	try:
		path = _data_path("hotels.json")
		with open(path, "r", encoding="utf-8") as f:
			hotels = json.load(f)
	except Exception as e:
		return f"Error reading hotels data: {e}"

	filtered = [
		h for h in hotels
		if str(h.get("city", "")).strip().title() == city
		and float(h.get("price_per_night_inr", float('inf'))) <= max_price
	]

	if preference and preference in preference_map:
		hotel_type = preference_map[preference]
		filtered = [h for h in filtered if h.get("type") == hotel_type]

	if not filtered:
		return f"No hotels found in {city} under ₹{int(max_price)} per night with preference '{preference}'."

	top3 = sorted(filtered, key=lambda x: float(x.get("rating", 0)), reverse=True)[:3]

	pref_txt = f" ({preference})" if preference else ""
	lines = [f"Top hotels in {city} under ₹{int(max_price)}{pref_txt}:"]
	for h in top3:
		lines.append(
			f"{h.get('hotel_id')} - {h.get('name')} | ₹{h.get('price_per_night_inr')}/night | "
			f"Rating: {h.get('rating')} | Type: {h.get('type')} | Amenities: {', '.join(h.get('amenities', []))}"
		)

	return "\n".join(lines)


@tool
def search_places(city: str) -> str:
	"""Search for tourist places in a city. Input: city name e.g. 'Goa'"""
	city = city.strip().title()
	try:
		path = _data_path("places.json")
		with open(path, "r", encoding="utf-8") as f:
			places = json.load(f)
	except Exception as e:
		return f"Error reading places data: {e}"

	filtered = [
		p for p in places
		if str(p.get("city", "")).strip().title() == city
	]

	if not filtered:
		return f"No attractions found for {city}."

	top5 = sorted(filtered, key=lambda x: float(x.get("rating", 0)), reverse=True)[:5]

	lines = [f"Top attractions in {city}:"]
	for p in top5:
		lines.append(
			f"{p.get('place_id')} - {p.get('name')} ({p.get('category')}) | Rating: {p.get('rating')} | "
			f"Entry: ₹{p.get('entry_fee_inr')} | Best: {p.get('best_time_to_visit')} — {p.get('description')}"
		)

	return "\n".join(lines)


def _map_weathercode(code: int) -> str:
	# Simplified mapping for common Open-Meteo weathercodes
	if code == 0:
		return "Clear"
	if code in (1, 2, 3):
		return "Partly cloudy"
	if code in (45, 48):
		return "Fog"
	if 51 <= code <= 67:
		return "Drizzle / Light rain"
	if 71 <= code <= 77:
		return "Snow"
	if 80 <= code <= 82:
		return "Rain showers"
	if 95 <= code <= 99:
		return "Thunderstorm"
	return "Unknown"


@tool
def get_weather(query: str) -> str:
	"""Get weather for a city. Input format: 'city,date' e.g. 'Goa,2026-05-21'"""
	parts = query.split(",")
	city = parts[0].strip().title()
	travel_date = parts[1].strip() if len(parts) > 1 else "2026-05-21"
	CITY_COORDINATES = {
		"Delhi": (28.6139, 77.2090),
		"Mumbai": (19.0760, 72.8777),
		"Goa": (15.2993, 74.1240),
		"Jaipur": (26.9124, 75.7873),
		"Manali": (32.2396, 77.1887),
		"Agra": (27.1767, 78.0081),
		"Kerala": (10.8505, 76.2711),
		"Coimbatore": (11.0168, 76.9558),
		"Chennai": (13.0827, 80.2707),
		"Thoothukudi": (8.7642, 78.1348),
		"Tuticorin": (8.7642, 78.1348),
		"Bangalore": (12.9716, 77.5946),
		"Bengaluru": (12.9716, 77.5946),
		"Hyderabad": (17.3850, 78.4867),
		"Pune": (18.5204, 73.8567),
		"Kolkata": (22.5726, 88.3639),
	}

	coords = CITY_COORDINATES.get(city)
	if coords is None:
		return f"City '{city}' not supported for weather lookup."

	try:
		# parse date
		date_obj = datetime.fromisoformat(travel_date).date()
		date_str = date_obj.isoformat()
	except Exception:
		return "Invalid date format. Use YYYY-MM-DD."

	lat, lon = coords
	url = "https://api.open-meteo.com/v1/forecast"
	params = {
		"latitude": lat,
		"longitude": lon,
		"daily": "temperature_2m_max,temperature_2m_min,weathercode",
		"start_date": date_str,
		"end_date": date_str,
		"timezone": "Asia/Kolkata",
	}

	try:
		resp = requests.get(url, params=params, timeout=10)
		resp.raise_for_status()
		data = resp.json()
	except Exception as e:
		return f"Weather API error: {e}"

	try:
		daily = data.get("daily", {})
		temps_max = daily.get("temperature_2m_max", [])
		temps_min = daily.get("temperature_2m_min", [])
		codes = daily.get("weathercode", [])

		if not temps_max or not temps_min:
			return f"No weather data available for {city} on {date_str}."

		tmax = temps_max[0]
		tmin = temps_min[0]
		code = int(codes[0]) if codes else -1
		condition = _map_weathercode(code)

		return (
			f"Weather in {city} on {date_str}: {condition}. "
			f"High: {tmax}°C, Low: {tmin}°C"
		)
	except Exception as e:
		return f"Error parsing weather data: {e}"


@tool
def estimate_budget(query: str) -> str:
	"""Estimate trip budget. Input format: 'flight_price,train_price,hotel_price,num_days' e.g. '4500,0,3000,3'
	Use 0 for either flight_price or train_price if not used."""
	parts = query.split(",")
	try:
		flight_price = int(parts[0].strip())
		train_price = int(parts[1].strip())
		hotel_price = int(parts[2].strip())
		num_days = int(parts[3].strip())
	except Exception:
		return "Invalid numeric inputs. Format: 'flight_price,train_price,hotel_price,num_days'."

	try:
		flight = float(flight_price)
		train = float(train_price)
		hotel = float(hotel_price)
		days = int(num_days)
	except Exception:
		return "Invalid numeric inputs."

	per_diem = 500
	accommodation = hotel * days
	incidental = per_diem * days

	# Transport cost is either flight or train (whichever is non-zero)
	transport = flight if flight > 0 else train
	transport_label = "Flight" if flight > 0 else "Train"

	total = transport + accommodation + incidental

	return (
		f"Budget estimate:\n"
		f"  {transport_label}: ₹{int(transport)}\n"
		f"  Hotel ({days} nights): ₹{int(accommodation)} (₹{int(hotel)}/night)\n"
		f"  Incidental (@₹{per_diem}/day): ₹{int(incidental)}\n"
		f"  ------------------------------\n"
		f"  Total estimated budget: ₹{int(total)}"
	)


@tool
def search_restaurants(query: str) -> str:
	"""Search for restaurants. Input format: 'city,cuisine_type' e.g. 'Goa,seafood'"""
	parts = query.split(",")
	city = parts[0].strip().title()
	cuisine = parts[1].strip().lower() if len(parts) > 1 else None

	try:
		path = _data_path("restaurants.json")
		with open(path, "r", encoding="utf-8") as f:
			restaurants = json.load(f)
	except Exception as e:
		return f"Error reading restaurants data: {e}"

	filtered = [
		r for r in restaurants
		if str(r.get("city", "")).strip().title() == city
	]

	if cuisine:
		filtered = [
			r for r in filtered
			if str(r.get("cuisine_type", "")).strip().lower() == cuisine
		]

	if not filtered:
		return f"No restaurants found in {city}" + (f" with {cuisine} cuisine." if cuisine else ".")

	top3 = sorted(filtered, key=lambda x: float(x.get("rating", 0)), reverse=True)[:3]

	cuisine_txt = f" ({cuisine})" if cuisine else ""
	lines = [f"Top restaurants in {city}{cuisine_txt}:"]
	for r in top3:
		veg_txt = "(Veg-friendly)" if r.get("vegetarian_friendly") else ""
		lines.append(
			f"{r.get('restaurant_id')} - {r.get('name')} {veg_txt} | ₹{r.get('avg_cost_per_person_inr')}/person | "
			f"Rating: {r.get('rating')} | {r.get('cuisine_type')} | {r.get('timings')}"
		)

	return "\n".join(lines)


@tool
def search_trains(query: str) -> str:
	"""Search for trains. Input format: 'source,destination' e.g. 'Chennai,Coimbatore'"""
	parts = query.split(",")
	source = parts[0].strip().title()
	destination = parts[1].strip().title()

	try:
		path = _data_path("trains.json")
		with open(path, "r", encoding="utf-8") as f:
			trains = json.load(f)
	except Exception as e:
		return f"Error reading trains data: {e}"

	matches = [
		t for t in trains
		if str(t.get("source", "")).strip().title() == source
		and str(t.get("destination", "")).strip().title() == destination
	]

	if not matches:
		return f"No trains found from {source} to {destination}."

	cheapest = min(matches, key=lambda x: float(x.get("price_inr", float('inf'))))
	return (
		f"Cheapest train {cheapest.get('train_id')} — {cheapest.get('train_name')} (#{cheapest.get('train_number')}): "
		f"{cheapest.get('source')} → {cheapest.get('destination')}, "
		f"Dep {cheapest.get('departure_time')}, Arr {cheapest.get('arrival_time')}, "
		f"Price: ₹{cheapest.get('price_inr')}, Duration: {cheapest.get('duration_hours')}h, "
		f"Class: {cheapest.get('class')}"
	)