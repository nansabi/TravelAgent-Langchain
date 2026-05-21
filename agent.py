"""
Agent runner for the travel_agent project.
Uses Groq LLaMA3 via LangGraph ReAct agent.
"""

import os
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


def get_agent_executor():
    api_key = get_api_key()
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in secrets or environment.")

    os.environ["GROQ_API_KEY"] = api_key

    from tools import (search_flights, search_hotels, search_places,
                       get_weather, estimate_budget,
                       search_restaurants, search_trains)

    from langchain_groq import ChatGroq
    from langgraph.prebuilt import create_react_agent

    tools = [search_flights, search_hotels, search_places,
             get_weather, estimate_budget,
             search_restaurants, search_trains]

    llm = ChatGroq(model="llama3-groq-70b-8192-tool-use-preview", temperature=0,
               api_key=api_key)

    system_prompt = """You are an expert AI travel planner for India.
Your job is to help users plan complete trips including flights, trains, hotels,
places to visit, restaurants, weather, and budget breakdown.
Always be helpful, detailed, and provide rupee costs.
Use the tools available to gather real information before answering.
Always call multiple tools to give a complete answer."""

    agent_executor = create_react_agent(
        llm,
        tools,
        prompt=system_prompt
    )

    return agent_executor


def run_travel_agent(user_query: str) -> str:
    """Run the travel planning agent and return the result."""
    try:
        agent_executor = get_agent_executor()
        result = agent_executor.invoke({
            "messages": [{"role": "user", "content": user_query}]
        })
        return result["messages"][-1].content
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