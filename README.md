# travel_agent

AI Travel Planning Assistant built with LangChain and Streamlit.

This repository contains the scaffold for a simple AI travel-planning assistant. It includes:

- `data/` — a folder for datasets, itineraries, or cached results.
- `.env` — place your `GROQ_API_KEY` here (you indicated you have a GROQ key instead of an OpenAI key).
- `requirements.txt` — Python dependencies.
- `tools.py`, `agent.py`, `app.py` — starter modules for building the agent and Streamlit app.

Getting started:

1. Create a Python virtual environment and activate it.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add your GROQ API key to `.env` as `GROQ_API_KEY`.
4. Implement the agent in `agent.py` and Streamlit UI in `app.py`.
