import streamlit as st
from agent import run_travel_agent, plan_multi_city_trip
import datetime
import urllib.parse
from pdf_generator import generate_trip_pdf

st.set_page_config(page_title="TRIPS — AI Travel Planner", page_icon="✈️", layout="wide")

if "history" not in st.session_state:
    st.session_state.history = []

# ============================================================
# CUSTOM CSS — Clean, Refined, Minimal
# Palette: #7F2020 (maroon), #869B7E (sage), #C9CAAC (tan), #F6F3EB (cream)
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --maroon:  #7F2020;
    --sage:    #869B7E;
    --tan:     #C9CAAC;
    --cream:   #F6F3EB;
    --dark:    #2A1A1A;
    --muted:   #6B5A5A;
}

* { font-family: 'DM Sans', sans-serif !important; }

/* ── App background ── */
.stApp {
    background-color: var(--cream) !important;
    min-height: 100vh;
}

/* ── Top nav bar ── */
.nav-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.1rem 2.5rem;
    background: white;
    border-bottom: 1px solid rgba(0,0,0,0.06);
    margin-bottom: 0;
}
.nav-logo {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.nav-logo-icon {
    width: 32px;
    height: 32px;
    background: var(--maroon);
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.9rem;
}
.nav-logo-text {
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 700;
    font-size: 1.1rem;
    letter-spacing: 0.15em;
    color: var(--dark);
}
.nav-links {
    display: flex;
    gap: 2.2rem;
    align-items: center;
}
.nav-link {
    color: var(--muted);
    font-size: 0.88rem;
    font-weight: 400;
    text-decoration: none;
    letter-spacing: 0.02em;
}
.nav-cta {
    background: var(--maroon);
    color: white !important;
    padding: 0.5rem 1.4rem;
    border-radius: 6px;
    font-size: 0.85rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* ── Hero ── */
.hero-section {
    position: relative;
    background: linear-gradient(160deg, #4a1515 0%, #7F2020 45%, #9B3A2A 100%);
    padding: 4.5rem 3rem 4rem;
    text-align: center;
    overflow: hidden;
}
.hero-section::before {
    content: '';
    position: absolute;
    inset: 0;
    background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}
.hero-eyebrow {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.6rem;
    margin-bottom: 1.2rem;
    font-size: 0.75rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--tan);
    font-weight: 500;
}
.hero-eyebrow-line {
    width: 40px;
    height: 1px;
    background: var(--tan);
    opacity: 0.6;
    display: inline-block;
}
.hero-title {
    font-family: 'Playfair Display', serif !important;
    font-size: 3.8rem;
    font-weight: 700;
    color: white;
    line-height: 1.1;
    margin: 0 0 1rem;
    letter-spacing: -0.02em;
}
.hero-title em {
    font-style: italic;
    color: var(--tan);
}
.hero-subtitle {
    color: rgba(255,255,255,0.65);
    font-size: 1rem;
    font-weight: 300;
    max-width: 480px;
    margin: 0 auto;
    line-height: 1.7;
}

/* ── Main layout ── */
.main-layout {
    display: grid;
    grid-template-columns: 380px 1fr;
    gap: 0;
    min-height: 60vh;
    background: var(--cream);
}

/* ── Form panel ── */
.form-panel-header {
    background: var(--maroon);
    padding: 1.2rem 1.6rem;
    border-radius: 12px 12px 0 0;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}
.form-panel-title {
    color: white;
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}

/* ── Input field overrides ── */
.stTextInput label,
.stNumberInput label,
.stDateInput label,
.stSelectbox label,
.stRadio label,
.stSelectSlider label,
.stCheckbox label {
    color: #555 !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stDateInput > div > div > input {
    background: white !important;
    border: 1px solid rgba(0,0,0,0.12) !important;
    border-radius: 8px !important;
    color: var(--dark) !important;
    font-size: 0.95rem !important;
    padding: 0.55rem 0.9rem !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--maroon) !important;
    box-shadow: 0 0 0 3px rgba(127,32,32,0.1) !important;
}

/* ── Radio buttons ── */
.stRadio > div > div {
    background: white !important;
    border: 1px solid rgba(0,0,0,0.1) !important;
    border-radius: 8px !important;
    padding: 0.35rem 0.9rem !important;
    margin-right: 0.4rem !important;
    font-size: 0.85rem !important;
    color: var(--dark) !important;
    transition: border-color 0.2s !important;
}

/* ── Select slider ── */
.stSelectSlider > div {
    background: transparent !important;
}

/* ── Submit button ── */
.stButton > button {
    background: var(--maroon) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.04em !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(127,32,32,0.25) !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #6a1a1a !important;
    box-shadow: 0 4px 16px rgba(127,32,32,0.35) !important;
    transform: translateY(-1px) !important;
}

/* ── Result panel ── */
.result-header {
    background: #2A1A1A;
    padding: 1.1rem 1.8rem;
    border-radius: 12px 12px 0 0;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.result-header-title {
    color: white;
    font-size: 0.95rem;
    font-weight: 500;
}
.ai-badge {
    background: var(--tan);
    color: var(--maroon);
    padding: 0.2rem 0.7rem;
    border-radius: 4px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* ── Trip summary bar ── */
.trip-summary-bar {
    background: #F0EBE3;
    border: 1px solid rgba(0,0,0,0.08);
    border-top: none;
    padding: 1rem 1.8rem;
    display: flex;
    gap: 2.5rem;
}
.summary-item-label {
    color: var(--muted);
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.15rem;
}
.summary-item-value {
    color: var(--dark);
    font-size: 0.9rem;
    font-weight: 500;
}

/* ── Metric cards ── */
.metric-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: rgba(0,0,0,0.08);
    border: 1px solid rgba(0,0,0,0.08);
    border-top: none;
    border-radius: 0;
    overflow: hidden;
}
.metric-item {
    background: #FAF7F2;
    padding: 1.2rem 1.5rem;
    text-align: center;
}
.metric-amount {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--maroon);
    letter-spacing: -0.02em;
}
.metric-desc {
    color: var(--muted);
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-top: 0.2rem;
}

/* ── Expanders ── */
.streamlit-expanderHeader {
    background: white !important;
    border: 1px solid rgba(0,0,0,0.08) !important;
    border-radius: 8px !important;
    color: var(--dark) !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    padding: 0.8rem 1.2rem !important;
}
.streamlit-expanderContent {
    background: white !important;
    border: 1px solid rgba(0,0,0,0.08) !important;
    border-top: none !important;
    border-radius: 0 0 8px 8px !important;
    padding: 1.2rem !important;
}

/* ── Result text box ── */
.result-box {
    background: white;
    border-left: 3px solid var(--maroon);
    border-radius: 0 6px 6px 0;
    padding: 1.2rem 1.5rem;
    color: var(--dark);
    font-size: 0.9rem;
    line-height: 1.85;
    white-space: pre-wrap;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: white !important;
    border-right: 1px solid rgba(0,0,0,0.07) !important;
}
section[data-testid="stSidebar"] * {
    color: var(--dark) !important;
}

/* ── Download / link buttons ── */
.stDownloadButton > button {
    background: var(--dark) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.04em !important;
}
.stLinkButton > a {
    background: var(--sage) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* ── Feedback / stars ── */
.stFeedback button {
    color: var(--maroon) !important;
}

/* ── Warning / error / success ── */
.stAlert {
    border-radius: 8px !important;
}
.stSuccess {
    background: rgba(134,155,126,0.12) !important;
    border: 1px solid rgba(134,155,126,0.4) !important;
    border-radius: 8px !important;
    color: var(--dark) !important;
}
.stWarning {
    background: rgba(201,202,172,0.25) !important;
    border: 1px solid var(--tan) !important;
    border-radius: 8px !important;
    color: var(--dark) !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--maroon) !important; }

/* ── Dividers ── */
hr {
    border: none !important;
    border-top: 1px solid rgba(0,0,0,0.08) !important;
    margin: 1.5rem 0 !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }

/* ── Section labels ── */
.section-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.6rem;
    display: block;
}

/* ── Checkbox ── */
.stCheckbox > label {
    color: var(--dark) !important;
    font-size: 0.88rem !important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# NAV BAR
# ============================================================
st.markdown("""
<div class="nav-bar">
    <div class="nav-logo">
        <div class="nav-logo-icon">🏠</div>
        <span class="nav-logo-text">TRIPS</span>
    </div>
    <div class="nav-links">
        <a class="nav-link" href="#">Home</a>
        <a class="nav-link" href="#">Destinations</a>
        <a class="nav-link" href="#">How It Works</a>
        <a class="nav-link" href="#">About</a>
        <a class="nav-link nav-cta" href="#">Plan a Trip</a>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# HERO
# ============================================================
st.markdown("""
<div class="hero-section">
    <div class="hero-eyebrow">
        <span class="hero-eyebrow-line"></span>
        AI Travel Agent
        <span class="hero-eyebrow-line"></span>
    </div>
    <h1 class="hero-title">Plan Your <em>Perfect</em> Journey</h1>
    <p class="hero-subtitle">Fill in your details below — our AI will craft a complete itinerary in seconds.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style="padding: 1.2rem 0 0.5rem;">
        <p style="font-size:0.7rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:#888; margin-bottom:0.8rem;">Suggested Trips</p>
    </div>
    """, unsafe_allow_html=True)

    sample_trips = [
        ("Delhi → Goa", "3 days"),
        ("Chennai → Coimbatore", "2 days"),
        ("Mumbai → Manali", "5 days"),
        ("Bangalore → Jaipur", "4 days"),
        ("Delhi → Kerala", "6 days"),
    ]
    for route, dur in sample_trips:
        st.markdown(f"""
        <div style="border:1px solid rgba(0,0,0,0.08); background:white; border-radius:8px;
        padding:0.6rem 0.9rem; margin:0.4rem 0; cursor:pointer;">
            <div style="font-size:0.88rem; font-weight:600; color:#2A1A1A;">{route}</div>
            <div style="font-size:0.72rem; color:#888; margin-top:0.1rem;">{dur}</div>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.history:
        st.markdown("""
        <div style="padding: 1rem 0 0.4rem;">
            <p style="font-size:0.7rem; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:#888; margin-bottom:0.6rem;">Recent Searches</p>
        </div>
        """, unsafe_allow_html=True)
        for h in reversed(st.session_state.history[-4:]):
            st.markdown(f"""
            <div style="font-size:0.8rem; color:#7F2020; padding:0.35rem 0;
            border-bottom:1px solid rgba(0,0,0,0.05);">↗ {h}</div>
            """, unsafe_allow_html=True)

# ============================================================
# TWO-COLUMN LAYOUT
# ============================================================
left_col, right_col = st.columns([4, 6], gap="large")

# ── LEFT: FORM ──────────────────────────────────────────────
with left_col:
    st.markdown("""
    <div class="form-panel-header">
        <span style="font-size:1.1rem;">📖</span>
        <span class="form-panel-title">Trip Details</span>
    </div>
    """, unsafe_allow_html=True)

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

        budget = st.number_input("Budget (INR)", min_value=1000, max_value=500000, value=10000, step=1000)

        st.markdown("<span class='section-label'>Transport Preference</span>", unsafe_allow_html=True)
        transport_mode = st.radio(
            "Transport",
            ["✈️ Flight", "🚂 Train", "🚌 Bus", "🔀 Either"],
            horizontal=True,
            label_visibility="collapsed"
        )

        st.markdown("<span class='section-label'>Trip Style</span>", unsafe_allow_html=True)
        trip_style = st.select_slider(
            "Style",
            options=["Budget", "Standard", "Comfort", "Premium", "Luxury"],
            value="Comfort",
            label_visibility="collapsed"
        )

        st.markdown("<span class='section-label'>Who's Travelling</span>", unsafe_allow_html=True)
        traveller_type = st.radio(
            "Traveller",
            ["Solo", "Couple", "Family", "Group"],
            horizontal=True,
            label_visibility="collapsed"
        )

        is_multi_city = st.checkbox("Multi-city trip?")
        if is_multi_city:
            stop2 = st.text_input("Second Stop", placeholder="e.g. Madurai")
        else:
            stop2 = None

        submitted = st.form_submit_button("✈️  Generate My Itinerary", use_container_width=True)

# ── RIGHT: RESULT ────────────────────────────────────────────
with right_col:
    if not submitted:
        # Placeholder state
        st.markdown("""
        <div style="background:white; border-radius:12px; border:1px solid rgba(0,0,0,0.08);
        padding:3rem 2rem; text-align:center; margin-top:0;">
            <div style="font-size:3rem; margin-bottom:1rem;">✈️</div>
            <p style="font-family:'Playfair Display',serif; font-size:1.5rem; color:#2A1A1A;
            font-weight:700; margin:0 0 0.5rem;">Your itinerary will appear here</p>
            <p style="color:#888; font-size:0.88rem; line-height:1.7;">
            Fill in your trip details on the left and click<br><b>Generate My Itinerary</b> to get started.</p>

            <div style="margin-top:2rem; display:flex; gap:1rem; justify-content:center; flex-wrap:wrap;">
                <div style="background:#F6F3EB; border-radius:8px; padding:0.8rem 1.2rem; min-width:110px;">
                    <div style="color:#7F2020; font-size:1.3rem; font-weight:700;">40+</div>
                    <div style="color:#888; font-size:0.7rem; letter-spacing:0.08em; text-transform:uppercase;">Destinations</div>
                </div>
                <div style="background:#F6F3EB; border-radius:8px; padding:0.8rem 1.2rem; min-width:110px;">
                    <div style="color:#7F2020; font-size:1.3rem; font-weight:700;">AI</div>
                    <div style="color:#888; font-size:0.7rem; letter-spacing:0.08em; text-transform:uppercase;">Powered</div>
                </div>
                <div style="background:#F6F3EB; border-radius:8px; padding:0.8rem 1.2rem; min-width:110px;">
                    <div style="color:#7F2020; font-size:1.3rem; font-weight:700;">Free</div>
                    <div style="color:#888; font-size:0.7rem; letter-spacing:0.08em; text-transform:uppercase;">To Use</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================================
# PROCESSING
# ============================================================
if submitted:
    if not source or not destination:
        st.warning("⚠️ Please enter both your origin and destination.")
    elif is_multi_city and not stop2:
        st.warning("⚠️ Please enter your second stop city.")
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
                st.session_state.history.append(f"{source} → {destination} → {stop2} ({num_days}d)")
            else:
                query = (
                    f"Plan a {num_days}-day {trip_style} style {traveller_type.lower()} trip to {destination} "
                    f"from {source} starting {travel_date} with a budget of ₹{budget}. "
                    f"Transport preference: {transport_mode}. "
                    f"Find transport options, recommend a hotel, suggest top places to visit, "
                    f"check the weather, recommend restaurants, and give a full budget breakdown."
                )
                with st.spinner("Your AI travel expert is crafting the perfect plan…"):
                    result = run_travel_agent(query)
                st.session_state.history.append(f"{source} → {destination} ({num_days}d)")

            with right_col:
                # Result header
                dest_label = f"{destination} → {stop2}" if is_multi_city else destination
                st.markdown(f"""
                <div class="result-header">
                    <span class="result-header-title">
                        {source.lower()} → {dest_label.lower()} — {num_days}-Day {trip_style} Trip
                    </span>
                    <span class="ai-badge">AI Generated</span>
                </div>
                """, unsafe_allow_html=True)

                # Summary bar
                transport_short = transport_mode.split()[-1]
                st.markdown(f"""
                <div class="trip-summary-bar">
                    <div>
                        <div class="summary-item-label">Origin</div>
                        <div class="summary-item-value">{source.lower()}</div>
                    </div>
                    <div>
                        <div class="summary-item-label">Destination</div>
                        <div class="summary-item-value">{destination.lower()}</div>
                    </div>
                    <div>
                        <div class="summary-item-label">Duration</div>
                        <div class="summary-item-value">{num_days} Days</div>
                    </div>
                    <div>
                        <div class="summary-item-label">Budget</div>
                        <div class="summary-item-value">₹{budget:,}</div>
                    </div>
                    <div>
                        <div class="summary-item-label">Transport</div>
                        <div class="summary-item-value">{transport_short}</div>
                    </div>
                    <div>
                        <div class="summary-item-label">Travelling</div>
                        <div class="summary-item-value">{traveller_type}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Metric cards
                transport_est = int(budget * 0.28)
                hotel_est = int(budget * 0.45)
                daily_est = budget // max(num_days, 1)
                st.markdown(f"""
                <div class="metric-row">
                    <div class="metric-item">
                        <div class="metric-amount">₹{transport_est:,}</div>
                        <div class="metric-desc">Transport Est.</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-amount">₹{hotel_est:,}</div>
                        <div class="metric-desc">Hotel Est.</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-amount">₹{daily_est:,}/day</div>
                        <div class="metric-desc">Daily Budget</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Itinerary sections
                sections = [
                    ("✈️", "Transport Details"),
                    ("🏨", "Hotel & Stay"),
                    ("🗺️", "Day-wise Itinerary"),
                    ("🌤️", "Weather Forecast"),
                    ("🍽️", "Restaurant Picks"),
                    ("💰", "Budget Breakdown"),
                ]

                if is_multi_city and "LEG 1:" in result and "LEG 2:" in result:
                    leg2_start = result.find("LEG 2:")
                    with st.expander(f"✈️  Leg 1 — {source} → {destination}", expanded=True):
                        st.markdown(f'<div class="result-box">{result[:leg2_start]}</div>', unsafe_allow_html=True)
                    with st.expander(f"✈️  Leg 2 — {destination} → {stop2}", expanded=True):
                        st.markdown(f'<div class="result-box">{result[leg2_start:]}</div>', unsafe_allow_html=True)
                else:
                    for icon, label in sections:
                        with st.expander(f"{icon}  {label}", expanded=(label == "Transport Details")):
                            st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)

                st.markdown("---")

                # Actions row
                a1, a2, a3 = st.columns(3)

                with a1:
                    try:
                        pdf_buffer = generate_trip_pdf(
                            itinerary_text=result,
                            source=source,
                            destination=destination,
                            num_days=num_days,
                            travel_date=str(travel_date),
                            budget=budget
                        )
                        st.download_button(
                            "📄 Download PDF",
                            data=pdf_buffer,
                            file_name="trip_itinerary.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    except Exception:
                        st.info("PDF export unavailable.")

                with a2:
                    share_msg = f"🌍 AI Trip Plan: {source} → {destination} for {num_days} days!\n\n{result[:300]}...\n\nPlanned by TRIPS AI ✈️"
                    whatsapp_url = f"https://wa.me/?text={urllib.parse.quote(share_msg)}"
                    st.link_button("📱 Share on WhatsApp", whatsapp_url, use_container_width=True)

                with a3:
                    if st.button("🔄 New Trip", use_container_width=True):
                        st.rerun()

                st.markdown("---")
                st.markdown("<h4 style='color:#2A1A1A; font-size:0.9rem;'>Rate this plan</h4>", unsafe_allow_html=True)
                rating = st.feedback("stars")
                if rating is not None:
                    st.success(f"{'⭐' * (rating + 1)}  Thanks for your feedback!")

                st.markdown("""
                <p style="color:#aaa; font-size:0.72rem; text-align:center; margin-top:1.5rem;">
                Always verify prices and availability before booking. Estimates are indicative only.
                </p>
                """, unsafe_allow_html=True)

                st.balloons()

        except Exception as e:
            st.error(f"Something went wrong. Please check your API configuration.\n\nError: {str(e)}")