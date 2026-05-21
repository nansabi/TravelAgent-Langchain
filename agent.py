"""
Agent runner for the travel_agent project.
Uses Groq SDK directly with manual tool calling loop.
"""

import os
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

        # Tool registry — all tools take a single string query
        tool_registry = {
            "search_flights": search_flights,
            "search_hotels": search_hotels,
            "search_places": search_places,
            "get_weather": get_weather,
            "estimate_budget": estimate_budget,
            "search_restaurants": search_restaurants,
            "search_trains": search_trains,
        }

        # Tool definitions — ALL take single "query" string to match your tools.py
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_flights",
                    "description": "Search for flights. Input: 'source,destination' e.g. 'Delhi,Goa'",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Format: 'source,destination' e.g. 'Delhi,Goa'"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_trains",
                    "description": "Search for trains. Input: 'source,destination' e.g. 'Chennai,Coimbatore'",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Format: 'source,destination' e.g. 'Chennai,Coimbatore'"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_hotels",
                    "description": "Search for hotels. Input: 'city,max_price,preference' e.g. 'Goa,5000,budget'",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Format: 'city,max_price,preference' e.g. 'Goa,5000,budget'"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_places",
                    "description": "Search tourist places in a city. Input: city name e.g. 'Goa'",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "City name e.g. 'Goa'"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_restaurants",
                    "description": "Search restaurants. Input: 'city,cuisine_type' e.g. 'Goa,seafood'",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Format: 'city,cuisine_type' e.g. 'Goa,seafood'"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather for a city. Input: 'city,date' e.g. 'Goa,2026-05-21'",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Format: 'city,date' e.g. 'Goa,2026-05-21'"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "estimate_budget",
                    "description": "Estimate trip budget. Input: 'flight_price,train_price,hotel_price,num_days' e.g. '4500,0,3000,3'",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Format: 'flight_price,train_price,hotel_price,num_days' e.g. '4500,0,3000,3'"
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
        ]

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert AI travel planner for India. "
                    "Help users plan complete trips. "
                    "Use tools one at a time in this order: "
                    "1) search_flights OR search_trains, "
                    "2) search_hotels, "
                    "3) search_places, "
                    "4) search_restaurants, "
                    "5) get_weather, "
                    "6) estimate_budget. "
                    "All tool inputs are a single comma-separated string called 'query'. "
                    "After all tools are called, give a complete day-by-day itinerary with budget breakdown in rupees."
                )
            },
            {"role": "user", "content": user_query}
        ]

        # Agentic loop
        for _ in range(15):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=4096,
            )

            msg = response.choices[0].message
            messages.append(msg)

            # No tool calls = final answer
            if not msg.tool_calls:
                return msg.content or "Sorry, could not generate a travel plan."

            # Execute each tool call
            for tool_call in msg.tool_calls:
                fn_name = tool_call.function.name
                try:
                    fn_args = json.loads(tool_call.function.arguments)
                except Exception:
                    fn_args = {}

                query_input = fn_args.get("query", "")
                fn = tool_registry.get(fn_name)

                if fn:
                    try:
                        # LangChain @tool uses .invoke()
                        result = fn.invoke(query_input)
                        tool_result = str(result)
                    except Exception as e:
                        tool_result = f"Tool error: {str(e)}"
                else:
                    tool_result = f"Tool '{fn_name}' not found."

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                })

        return "Sorry, could not complete the travel plan. Please try again."

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