import streamlit as st
from agent import run_travel_agent, plan_multi_city_trip
import datetime
import urllib.parse
from pdf_generator import generate_trip_pdf

st.set_page_config(
    page_title="TRIPS — AI Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "history" not in st.session_state:
    st.session_state.history = []
if "result" not in st.session_state:
    st.session_state.result = None
if "trip_meta" not in st.session_state:
    st.session_state.trip_meta = {}

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=DM+Sans:opsz,wght@9..40,300;9..40,400;9..40,500;9..40,600&display=swap');

:root {
    --maroon: #7F2020;
    --maroon-dark: #5C1515;
    --sage: #869B7E;
    --tan: #C9CAAC;
    --cream: #F6F3EB;
    --ink: #1E1212;
    --muted: #7A6A6A;
    --border: rgba(0,0,0,0.09);
    --white: #FFFFFF;
}

* { font-family: 'DM Sans', sans-serif !important; box-sizing: border-box; }

/* Background */
.stApp { background: var(--cream) !important; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; padding-bottom: 2rem !important; max-width: 100% !important; }

/* ── HERO ── */
.hero {
    background: var(--maroon);
    padding: 3rem 3.5rem 2.8rem;
    margin: 0 0 2rem;
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: '';
    position: absolute;
    right: -60px; top: -60px;
    width: 280px; height: 280px;
    border-radius: 50%;
    background: rgba(255,255,255,0.04);
    pointer-events: none;
}
.hero-label {
    font-size: 0.68rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--tan);
    font-weight: 600;
    margin-bottom: 0.7rem;
}
.hero h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 2.8rem;
    font-weight: 700;
    color: #fff;
    line-height: 1.15;
    margin: 0 0 0.6rem;
    letter-spacing: -0.01em;
}
.hero h1 em { font-style: italic; color: var(--tan); }
.hero p {
    color: rgba(255,255,255,0.55);
    font-size: 0.92rem;
    font-weight: 300;
    margin: 0;
    line-height: 1.6;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: var(--white) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] > div { padding: 1.5rem 1.2rem !important; }
.sidebar-section-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.75rem;
    display: block;
}
.trip-chip {
    background: var(--cream);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.6rem 0.9rem;
    margin-bottom: 0.4rem;
}
.trip-chip-route { font-size: 0.88rem; font-weight: 600; color: var(--ink); }
.trip-chip-dur   { font-size: 0.72rem; color: var(--muted); margin-top: 0.1rem; }
.history-item {
    font-size: 0.8rem;
    color: var(--maroon);
    padding: 0.3rem 0;
    border-bottom: 1px solid var(--border);
}

/* ── FORM PANEL ── */
.form-header {
    background: var(--maroon);
    border-radius: 10px 10px 0 0;
    padding: 1rem 1.4rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0;
}
.form-header-text {
    color: white;
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.form-body {
    background: white;
    border: 1px solid var(--border);
    border-top: none;
    border-radius: 0 0 10px 10px;
    padding: 1.4rem;
}

/* ── FIELD LABELS ── */
.stTextInput label, .stNumberInput label,
.stDateInput label, .stRadio > label,
.stSelectSlider > label, .stCheckbox > label {
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
    margin-bottom: 0.3rem !important;
}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput input {
    background: var(--cream) !important;
    border: 1px solid var(--border) !important;
    border-radius: 7px !important;
    color: var(--ink) !important;
    font-size: 0.92rem !important;
    padding: 0.52rem 0.85rem !important;
    transition: border-color 0.15s !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--maroon) !important;
    box-shadow: 0 0 0 2px rgba(127,32,32,0.12) !important;
}

/* ── RADIO ── */
.stRadio > div { gap: 0.4rem !important; flex-wrap: wrap !important; }
.stRadio > div > label {
    background: var(--cream) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    padding: 0.35rem 0.85rem !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    color: var(--ink) !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
    cursor: pointer !important;
    transition: border-color 0.15s, background 0.15s !important;
}
.stRadio > div > label:has(input:checked) {
    border-color: var(--maroon) !important;
    background: rgba(127,32,32,0.06) !important;
    color: var(--maroon) !important;
    font-weight: 600 !important;
}

/* ── SELECT SLIDER ── */
.stSlider > div > div > div > div { background: var(--maroon) !important; }
.stSlider > div > div > div { background: var(--tan) !important; }

/* ── SUBMIT BUTTON ── */
.stFormSubmitButton > button,
div[data-testid="stFormSubmitButton"] > button {
    background: var(--ink) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.72rem 1.4rem !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.05em !important;
    transition: background 0.2s, transform 0.15s !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.18) !important;
    width: 100% !important;
    margin-top: 0.5rem !important;
}
.stFormSubmitButton > button:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    background: var(--maroon) !important;
    transform: translateY(-1px) !important;
}

/* ── OTHER BUTTONS ── */
.stButton > button {
    background: var(--ink) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.04em !important;
    padding: 0.6rem 1.2rem !important;
    transition: background 0.2s !important;
}
.stButton > button:hover { background: var(--maroon) !important; }

.stDownloadButton > button {
    background: var(--ink) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.82rem !important;
}

/* ── RESULT CARD ── */
.result-card-header {
    background: var(--ink);
    border-radius: 10px 10px 0 0;
    padding: 1rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.result-card-title { color: white; font-size: 0.92rem; font-weight: 500; }
.ai-tag {
    background: var(--tan);
    color: var(--maroon);
    font-size: 0.64rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.22rem 0.65rem;
    border-radius: 4px;
}

/* ── SUMMARY BAR ── */
.summary-bar {
    background: #EDE9DF;
    border: 1px solid var(--border);
    border-top: none;
    padding: 0.9rem 1.5rem;
    display: flex;
    flex-wrap: wrap;
    gap: 2rem;
}
.summary-item { line-height: 1; }
.summary-label { font-size: 0.62rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); }
.summary-value { font-size: 0.88rem; font-weight: 600; color: var(--ink); margin-top: 0.25rem; }

/* ── METRICS ── */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(3,1fr);
    border: 1px solid var(--border);
    border-top: none;
    border-radius: 0;
    overflow: hidden;
}
.metric-cell {
    background: #FAF8F3;
    padding: 1.1rem 1rem;
    text-align: center;
    border-right: 1px solid var(--border);
}
.metric-cell:last-child { border-right: none; }
.metric-num {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--maroon);
    letter-spacing: -0.02em;
}
.metric-lbl {
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 0.25rem;
}

/* ── EXPANDERS ── */
details[data-testid="stExpander"] {
    background: white !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    margin-bottom: 0.5rem !important;
}
details[data-testid="stExpander"] summary {
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    color: var(--ink) !important;
    padding: 0.85rem 1.1rem !important;
    background: white !important;
}
details[data-testid="stExpander"] summary:hover {
    background: var(--cream) !important;
}
details[data-testid="stExpander"] > div {
    padding: 0 !important;
    background: white !important;
}

/* ── RESULT TEXT ── */
.result-text {
    border-left: 3px solid var(--maroon);
    background: white;
    padding: 1.1rem 1.3rem;
    color: var(--ink);
    font-size: 0.88rem;
    line-height: 1.9;
    white-space: pre-wrap;
    border-radius: 0 6px 6px 0;
}

/* ── DIVIDER ── */
hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.2rem 0 !important; }

/* ── ALERTS ── */
.stWarning, .stError {
    border-radius: 8px !important;
    font-size: 0.88rem !important;
}
.stSuccess {
    background: rgba(134,155,126,0.1) !important;
    border: 1px solid rgba(134,155,126,0.35) !important;
    border-radius: 8px !important;
    color: var(--ink) !important;
}
.stSpinner > div { border-top-color: var(--maroon) !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# HERO (no nav — just clean title)
# ============================================================
st.markdown("""
<div class="hero">
    <div class="hero-label">✦ AI Travel Agent</div>
    <h1>Plan Your <em>Perfect</em> Journey</h1>
    <p>Fill in your details — our AI crafts a complete itinerary in seconds.</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown('<span class="sidebar-section-label">Suggested Trips</span>', unsafe_allow_html=True)
    trips = [
        ("Delhi → Goa", "3 days"),
        ("Chennai → Coimbatore", "2 days"),
        ("Mumbai → Manali", "5 days"),
        ("Bangalore → Jaipur", "4 days"),
        ("Delhi → Kerala", "6 days"),
    ]
    for route, dur in trips:
        st.markdown(f"""
        <div class="trip-chip">
            <div class="trip-chip-route">{route}</div>
            <div class="trip-chip-dur">{dur}</div>
        </div>""", unsafe_allow_html=True)

    if st.session_state.history:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<span class="sidebar-section-label">Recent Searches</span>', unsafe_allow_html=True)
        for h in reversed(st.session_state.history[-5:]):
            st.markdown(f'<div class="history-item">↗ {h}</div>', unsafe_allow_html=True)

# ============================================================
# MAIN: TWO COLUMNS
# ============================================================
left, right = st.columns([4, 6], gap="large")

# ── LEFT COLUMN: FORM ──────────────────────────────────────
with left:
    st.markdown("""
    <div class="form-header">
        <span>📖</span>
        <span class="form-header-text">Trip Details</span>
    </div>
    <div style="height:0;"></div>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        with st.form("trip_form"):
            c1, c2 = st.columns(2)
            with c1:
                source = st.text_input("From", placeholder="e.g. Thoothukudi")
            with c2:
                destination = st.text_input("To", placeholder="e.g. Chennai")

            c3, c4 = st.columns(2)
            with c3:
                travel_date = st.date_input("Start Date", min_value=datetime.date.today())
            with c4:
                num_days = st.number_input("Number of Days", min_value=1, max_value=14, value=1)

            budget = st.number_input("Budget (INR)", min_value=1000, max_value=500000,
                                     value=10000, step=1000)

            transport_mode = st.radio(
                "Transport Preference",
                ["✈️ Flight", "🚂 Train", "🚌 Bus", "🔀 Either"],
                horizontal=True
            )

            trip_style = st.select_slider(
                "Trip Style",
                options=["Budget", "Standard", "Comfort", "Premium", "Luxury"],
                value="Comfort"
            )

            traveller_type = st.radio(
                "Who's Travelling",
                ["Solo", "Couple", "Family", "Group"],
                horizontal=True
            )

            is_multi_city = st.checkbox("Multi-city trip?")
            stop2 = None
            if is_multi_city:
                stop2 = st.text_input("Second Stop", placeholder="e.g. Madurai")

            submitted = st.form_submit_button("✈️  Generate My Itinerary",
                                              use_container_width=True)

# ── RIGHT COLUMN: RESULT ───────────────────────────────────
with right:
    if st.session_state.result is None:
        # Clean placeholder — native Streamlit only, no raw HTML
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(
            "<h3 style='text-align:center; font-family:Playfair Display,serif; "
            "color:#1E1212; font-weight:700; font-size:1.6rem;'>"
            "✈️ Your itinerary will appear here</h3>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='text-align:center; color:#7A6A6A; font-size:0.88rem; line-height:1.7;'>"
            "Fill in your trip details on the left and click<br>"
            "<strong>Generate My Itinerary</strong> to get started.</p>",
            unsafe_allow_html=True
        )
    else:
        meta   = st.session_state.trip_meta
        result = st.session_state.result

        transport_short = meta.get("transport", "").split()[-1]
        dest_label      = meta.get("dest_label", meta.get("destination", ""))

        # Header
        st.markdown(f"""
        <div class="result-card-header">
            <span class="result-card-title">
                {meta.get('source','').lower()} → {dest_label.lower()} &nbsp;—&nbsp;
                {meta.get('num_days','')} Day {meta.get('trip_style','')} Trip
            </span>
            <span class="ai-tag">AI Generated</span>
        </div>""", unsafe_allow_html=True)

        # Summary bar
        st.markdown(f"""
        <div class="summary-bar">
            <div class="summary-item">
                <div class="summary-label">Origin</div>
                <div class="summary-value">{meta.get('source','').lower()}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Destination</div>
                <div class="summary-value">{meta.get('destination','').lower()}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Duration</div>
                <div class="summary-value">{meta.get('num_days','')} Days</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Budget</div>
                <div class="summary-value">₹{meta.get('budget',0):,}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Transport</div>
                <div class="summary-value">{transport_short}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">Travelling</div>
                <div class="summary-value">{meta.get('traveller','')}</div>
            </div>
        </div>""", unsafe_allow_html=True)

        # Metric row
        b = meta.get('budget', 10000)
        n = max(meta.get('num_days', 1), 1)
        st.markdown(f"""
        <div class="metrics-row">
            <div class="metric-cell">
                <div class="metric-num">₹{int(b*0.28):,}</div>
                <div class="metric-lbl">Transport Est.</div>
            </div>
            <div class="metric-cell">
                <div class="metric-num">₹{int(b*0.45):,}</div>
                <div class="metric-lbl">Hotel Est.</div>
            </div>
            <div class="metric-cell">
                <div class="metric-num">₹{b//n:,}/day</div>
                <div class="metric-lbl">Daily Budget</div>
            </div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Itinerary sections
        sections = [
            ("✈️  Transport Details", True),
            ("🏨  Hotel & Stay", False),
            ("🗺️  Day-wise Itinerary", False),
            ("🌤️  Weather Forecast", False),
            ("🍽️  Restaurant Picks", False),
            ("💰  Budget Breakdown", False),
        ]

        if meta.get("is_multi_city") and "LEG 1:" in result and "LEG 2:" in result:
            split = result.find("LEG 2:")
            with st.expander(f"✈️  Leg 1 — {meta['source']} → {meta['destination']}", expanded=True):
                st.markdown(f'<div class="result-text">{result[:split]}</div>', unsafe_allow_html=True)
            with st.expander(f"✈️  Leg 2 — {meta['destination']} → {meta.get('stop2','')}", expanded=True):
                st.markdown(f'<div class="result-text">{result[split:]}</div>', unsafe_allow_html=True)
        else:
            for label, expanded in sections:
                with st.expander(label, expanded=expanded):
                    st.markdown(f'<div class="result-text">{result}</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Action row
        a1, a2, a3 = st.columns(3)
        with a1:
            try:
                pdf_buf = generate_trip_pdf(
                    itinerary_text=result,
                    source=meta['source'],
                    destination=meta['destination'],
                    num_days=meta['num_days'],
                    travel_date=str(meta['travel_date']),
                    budget=meta['budget']
                )
                st.download_button("📄 Download PDF", data=pdf_buf,
                                   file_name="itinerary.pdf", mime="application/pdf",
                                   use_container_width=True)
            except Exception:
                pass
        with a2:
            msg = f"🌍 {meta.get('source','')} → {meta.get('destination','')} · {meta.get('num_days','')} days\n\n{result[:300]}...\n\nPlanned by TRIPS AI ✈️"
            st.link_button("📱 Share on WhatsApp",
                           f"https://wa.me/?text={urllib.parse.quote(msg)}",
                           use_container_width=True)
        with a3:
            if st.button("↺  New Trip", use_container_width=True):
                st.session_state.result   = None
                st.session_state.trip_meta = {}
                st.rerun()

        st.markdown("---")
        rating = st.feedback("stars")
        if rating is not None:
            st.success(f"{'⭐' * (rating+1)}  Thanks for your feedback!")

        st.caption("Always verify prices and availability before booking.")
        st.balloons()

# ============================================================
# HANDLE FORM SUBMISSION
# ============================================================
if submitted:
    if not source or not destination:
        st.warning("Please enter both your origin and destination.")
    elif is_multi_city and not stop2:
        st.warning("Please enter your second stop city.")
    else:
        try:
            if is_multi_city:
                with st.spinner("Crafting your multi-city adventure…"):
                    result = plan_multi_city_trip(
                        source=source,
                        destination1=destination,
                        destination2=stop2,
                        travel_date=str(travel_date),
                        num_days=num_days,
                        budget=budget
                    )
                st.session_state.history.append(
                    f"{source} → {destination} → {stop2} ({num_days}d)")
            else:
                query = (
                    f"Plan a {num_days}-day {trip_style} {traveller_type.lower()} trip to "
                    f"{destination} from {source} starting {travel_date} with ₹{budget} budget. "
                    f"Transport: {transport_mode}. Find transport, recommend hotel, "
                    f"top places, weather, restaurants, full budget breakdown."
                )
                with st.spinner("Your AI travel expert is planning your trip…"):
                    result = run_travel_agent(query)
                st.session_state.history.append(f"{source} → {destination} ({num_days}d)")

            st.session_state.result = result
            st.session_state.trip_meta = {
                "source": source,
                "destination": destination,
                "dest_label": f"{destination} → {stop2}" if is_multi_city else destination,
                "stop2": stop2,
                "num_days": num_days,
                "budget": budget,
                "transport": transport_mode,
                "trip_style": trip_style,
                "traveller": traveller_type,
                "travel_date": travel_date,
                "is_multi_city": is_multi_city,
            }
            st.rerun()

        except Exception as e:
            st.error(f"Something went wrong. Check your API configuration.\n\nError: {e}")