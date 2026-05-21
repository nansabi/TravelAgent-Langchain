"""
Agent runner for the travel_agent project.
Direct tool calling — no LLM tool-use API, zero token waste.
"""

import os
import re
import json
from dotenv import load_dotenv

load_dotenv()


def get_api_key():
    try:
        import streamlit as st
        key = st.secrets.get("GROQ_API_KEY", "")
        if key:
            return key
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY", "")


def extract_trip_info(query: str) -> dict:
    """Extract source, destination, days, budget, date from query string."""
    import datetime

    query_lower = query.lower()

    # Extract days
    days_match = re.search(r'(\d+)\s*day', query_lower)
    num_days = int(days_match.group(1)) if days_match else 3

    # Extract budget
    budget_match = re.search(r'(\d+)\s*rupee', query_lower)
    budget = int(budget_match.group(1)) if budget_match else 20000

    # Extract date
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', query)
    travel_date = date_match.group(1) if date_match else datetime.date.today().isoformat()

    # Extract source and destination
    # Pattern: "to X from Y" or "from Y to X"
    to_from = re.search(r'to\s+([a-zA-Z]+)\s+from\s+([a-zA-Z]+)', query_lower)
    from_to = re.search(r'from\s+([a-zA-Z]+)\s+to\s+([a-zA-Z]+)', query_lower)

    if to_from:
        destination = to_from.group(1).title()
        source = to_from.group(2).title()
    elif from_to:
        source = from_to.group(1).title()
        destination = from_to.group(2).title()
    else:
        source = "Delhi"
        destination = "Goa"

    # Determine transport preference
    transport = "flight"
    if any(w in query_lower for w in ["train", "railway", "rail"]):
        transport = "train"
    elif any(w in query_lower for w in ["bus", "drive", "road"]):
        transport = "bus"

    # Trip style
    style = "standard"
    for s in ["budget", "luxury", "comfort", "premium"]:
        if s in query_lower:
            style = s
            break

    return {
        "source": source,
        "destination": destination,
        "num_days": num_days,
        "budget": budget,
        "travel_date": travel_date,
        "transport": transport,
        "style": style,
    }


def run_travel_agent(user_query: str) -> str:
    """Run the travel planning agent and return the result."""
    try:
        from groq import Groq
        from tools import (search_flights, search_hotels, search_places,
                           get_weather, estimate_budget,
                           search_restaurants, search_trains)

        api_key = get_api_key()
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in secrets or environment.")

        client = Groq(api_key=api_key)

        # Step 1: Extract trip info directly from query
        info = extract_trip_info(user_query)
        src = info["source"]
        dst = info["destination"]
        days = info["num_days"]
        budget = info["budget"]
        date = info["travel_date"]
        transport = info["transport"]
        style = info["style"]

        hotel_budget = int(budget * 0.4 / days)

        # Step 2: Call all tools directly — no LLM tool-use
        results = {}

        # Flights or trains
        if transport == "train":
            results["transport"] = search_trains.invoke(f"{src},{dst}")
        else:
            flight_result = search_flights.invoke(f"{src},{dst}")
            if "No flights found" in flight_result:
                results["transport"] = search_trains.invoke(f"{src},{dst}")
                transport = "train"
            else:
                results["transport"] = flight_result

        results["hotels"] = search_hotels.invoke(f"{dst},{hotel_budget},{style}")
        results["places"] = search_places.invoke(dst)
        results["restaurants"] = search_restaurants.invoke(f"{dst},indian")
        results["weather"] = get_weather.invoke(f"{dst},{date}")

        # Extract transport cost for budget
        transport_cost = 0
        cost_match = re.search(r'₹([\d,]+)', results["transport"])
        if cost_match:
            transport_cost = int(cost_match.group(1).replace(",", ""))

        hotel_cost = hotel_budget
        hotel_match = re.search(r'₹([\d,]+)/night', results["hotels"])
        if hotel_match:
            hotel_cost = int(hotel_match.group(1).replace(",", ""))

        if transport == "train":
            results["budget"] = estimate_budget.invoke(f"0,{transport_cost},{hotel_cost},{days}")
        else:
            results["budget"] = estimate_budget.invoke(f"{transport_cost},0,{hotel_cost},{days}")

        # Step 3: Ask LLM to synthesize everything into a nice itinerary
        synthesis_prompt = f"""You are an expert travel planner. Based on the data below, write a complete, 
friendly {days}-day trip itinerary from {src} to {dst}.

TRANSPORT: {results['transport']}

HOTELS: {results['hotels']}

PLACES TO VISIT: {results['places']}

RESTAURANTS: {results['restaurants']}

WEATHER: {results['weather']}

BUDGET: {results['budget']}

Write a day-by-day plan using the above info. Include:
- Transport details (flight/train)
- Hotel recommendation  
- Day-wise activities using the places listed
- Restaurant suggestions
- Weather advisory
- Final budget summary

Keep it friendly, detailed and practical. Use rupee (₹) for all costs."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a friendly expert travel planner for India."},
                {"role": "user", "content": synthesis_prompt}
            ],
            max_tokens=2048,
            temperature=0.7,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Agent error: {str(e)}"


def plan_multi_city_trip(source: str, destination1: str, destination2: str,
                         travel_date: str, num_days: int, budget: int) -> str:
    """Plan a multi-city trip across two destinations."""
    import datetime

    if num_days < 2:
        return "Multi-city trips require at least 2 days."

    days_per_leg = num_days // 2
    remaining_days = num_days % 2
    leg1_days = days_per_leg + remaining_days
    leg2_days = days_per_leg

    leg1_budget = int(budget * (leg1_days / num_days))
    leg2_budget = int(budget * (leg2_days / num_days))

    start_dt = datetime.datetime.fromisoformat(travel_date)
    leg2_start = (start_dt + datetime.timedelta(days=leg1_days)).strftime("%Y-%m-%d")

    leg1_query = (
        f"Plan a {leg1_days} day trip to {destination1} from {source} "
        f"starting {travel_date} with a budget of {leg1_budget} rupees. "
        f"Suggest flights, hotels, places to visit, weather, and budget breakdown."
    )
    leg2_query = (
        f"Plan a {leg2_days} day trip to {destination2} from {destination1} "
        f"starting {leg2_start} with a budget of {leg2_budget} rupees. "
        f"Suggest flights, hotels, places to visit, weather, and budget breakdown."
    )

    leg1_result = run_travel_agent(leg1_query)
    leg2_result = run_travel_agent(leg2_query)

    combined = (
        f"\n{'='*70}\n"
        f"🌍 MULTI-CITY TRIP: {source} → {destination1} → {destination2}\n"
        f"{'='*70}\n\n"
        f"📍 === LEG 1: {source} to {destination1} (Day 1-{leg1_days}) ===\n"
        f"{'─'*70}\n"
        f"{leg1_result}\n\n"
        f"📍 === LEG 2: {destination1} to {destination2} "
        f"(Day {leg1_days+1}-{num_days}) ===\n"
        f"{'─'*70}\n"
        f"{leg2_result}\n\n"
        f"{'='*70}\n"
        f"✅ End of Multi-City Itinerary\n"
        f"{'='*70}\n"
    )
    return combined


if __name__ == "__main__":
    query = "Plan a 3 day trip to Goa from Delhi with a budget of 20000 rupees"
    print(run_travel_agent(query))