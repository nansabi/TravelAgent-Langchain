"""
Agent runner for the travel_agent project.

This module constructs a ReAct-style LangChain agent using the Groq LLM
backend and the tools defined in `tools.py`. It exposes `run_travel_agent()`
which accepts a user query and returns the agent's textual output.
"""

from dotenv import load_dotenv
import os

load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

from tools import search_flights, search_hotels, search_places, get_weather, estimate_budget, search_restaurants, search_trains

tools = [search_flights, search_hotels, search_places, get_weather, estimate_budget, search_restaurants, search_trains]

from langchain_groq import ChatGroq

# Configure Groq LLM
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

from langchain import hub
from langchain.agents import create_react_agent, AgentExecutor

# Pull the ReAct-style prompt and create the agent
prompt = hub.pull("hwchase17/react")
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=10,
)


def run_travel_agent(user_query: str) -> str:
    """Run the travel planning agent on `user_query` and return textual output.

    The function invokes the `agent_executor` and returns the agent's
    `output` field. Any exceptions are caught and returned as an error string.
    """
    try:
        result = agent_executor.invoke({"input": user_query})
        return result["output"]
    except Exception as e:
        return f"Agent error: {str(e)}"


def plan_multi_city_trip(source: str, destination1: str, destination2: str, 
                         travel_date: str, num_days: int, budget: int) -> str:
    """Plan a multi-city trip with stops at destination1 then destination2.
    
    Splits the travel days equally across legs and calls run_travel_agent
    for each leg, then combines results into a structured itinerary.
    
    Args:
        source: Starting city
        destination1: First stop city
        destination2: Second stop city
        travel_date: Start date (YYYY-MM-DD format)
        num_days: Total number of travel days
        budget: Total budget in rupees
        
    Returns:
        Combined itinerary with section headers for each leg.
    """
    import datetime
    
    if num_days < 2:
        return "Multi-city trips require at least 2 days."
    
    # Split days equally between legs
    days_per_leg = num_days // 2
    remaining_days = num_days % 2
    
    leg1_days = days_per_leg + remaining_days
    leg2_days = days_per_leg
    
    # Split budget proportionally
    leg1_budget = int(budget * (leg1_days / num_days))
    leg2_budget = int(budget * (leg2_days / num_days))
    
    # Calculate leg2 start date
    start_dt = datetime.datetime.fromisoformat(travel_date)
    leg2_start_date = (start_dt + datetime.timedelta(days=leg1_days)).strftime("%Y-%m-%d")
    
    # Build queries for each leg
    leg1_query = (
        f"Plan a {leg1_days} day trip to {destination1} from {source} "
        f"starting {travel_date} with a budget of {leg1_budget} rupees. "
        f"Suggest flights, hotels, places to visit, weather, and budget breakdown."
    )
    
    leg2_query = (
        f"Plan a {leg2_days} day trip to {destination2} from {destination1} "
        f"starting {leg2_start_date} with a budget of {leg2_budget} rupees. "
        f"Suggest flights, hotels, places to visit, weather, and budget breakdown."
    )
    
    # Run agent for each leg
    leg1_result = run_travel_agent(leg1_query)
    leg2_result = run_travel_agent(leg2_query)
    
    # Combine results
    combined = (
        f"\n{'='*70}\n"
        f"🌍 MULTI-CITY TRIP ITINERARY: {source} → {destination1} → {destination2}\n"
        f"{'='*70}\n\n"
        f"📍 === LEG 1: {source} to {destination1} (Day 1-{leg1_days}) ===\n"
        f"{'─'*70}\n"
        f"{leg1_result}\n\n"
        f"📍 === LEG 2: {destination1} to {destination2} (Day {leg1_days+1}-{num_days}) ===\n"
        f"{'─'*70}\n"
        f"{leg2_result}\n\n"
        f"{'='*70}\n"
        f"✅ End of Multi-City Itinerary\n"
        f"{'='*70}\n"
    )
    
    return combined


if __name__ == "__main__":
    query = "Plan a 3 day trip to Goa from Delhi in February with a budget of 20000 rupees"
    print(run_travel_agent(query))
