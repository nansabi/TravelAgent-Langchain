"""
Agent runner for the travel_agent project.
Uses Groq LLaMA3 via LangChain ReAct agent.
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
    from langchain_core.prompts import PromptTemplate
    from langchain_core.agents import create_react_agent
    from langchain.agents import AgentExecutor

    tools = [search_flights, search_hotels, search_places,
             get_weather, estimate_budget,
             search_restaurants, search_trains]

    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0,
                   api_key=api_key)

    prompt = PromptTemplate.from_template("""Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}""")

    agent = create_react_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=10,
    )
    return agent_executor


def run_travel_agent(user_query: str) -> str:
    """Run the travel planning agent and return the result."""
    try:
        agent_executor = get_agent_executor()
        result = agent_executor.invoke({"input": user_query})
        return result["output"]
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