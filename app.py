import streamlit as st
from agent import run_travel_agent, plan_multi_city_trip
import datetime
import urllib.parse
from pdf_generator import generate_trip_pdf

st.set_page_config(page_title="AI Travel Planner ✈️", page_icon="✈️", layout="wide")

if "history" not in st.session_state:
    st.session_state.history = []

# ============================================================
# CUSTOM CSS - Full Vibey Styling
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap');

* { font-family: 'Poppins', sans-serif !important; }

.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

/* Hero Banner */
.hero {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 50%, #4facfe 100%);
    padding: 3rem 2rem;
    border-radius: 25px;
    text-align: center;
    margin-bottom: 2rem;
    animation: heroGlow 3s ease-in-out infinite alternate;
    box-shadow: 0 20px 60px rgba(240, 147, 251, 0.3);
}

@keyframes heroGlow {
    from { box-shadow: 0 20px 60px rgba(240, 147, 251, 0.3); }
    to   { box-shadow: 0 20px 80px rgba(79, 172, 254, 0.5); }
}

.hero h1 {
    font-size: 3.5rem;
    font-weight: 800;
    color: white;
    margin: 0;
    text-shadow: 2px 2px 20px rgba(0,0,0,0.3);
    letter-spacing: -1px;
}

.hero p {
    color: rgba(255,255,255,0.9);
    font-size: 1.2rem;
    margin-top: 0.5rem;
}

.hero .badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    color: white;
    padding: 0.3rem 1rem;
    border-radius: 50px;
    font-size: 0.85rem;
    margin-top: 0.5rem;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.3);
}

/* Floating emoji animation */
@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50%       { transform: translateY(-10px); }
}

.float-emoji {
    display: inline-block;
    animation: float 2s ease-in-out infinite;
    font-size: 3rem;
}

/* Glass card */
.glass-card {
    background: rgba(255,255,255,0.05);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px;
    padding: 1.5rem;
    margin: 1rem 0;
}

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, rgba(240,147,251,0.15), rgba(79,172,254,0.15));
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 15px;
    padding: 1.2rem;
    text-align: center;
    transition: transform 0.3s ease;
}

.metric-card:hover { transform: translateY(-5px); }

.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #f093fb, #4facfe);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.metric-label {
    color: rgba(255,255,255,0.6);
    font-size: 0.85rem;
    margin-top: 0.2rem;
}

/* Result box */
.result-box {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-left: 4px solid #f093fb;
    border-radius: 15px;
    padding: 2rem;
    color: rgba(255,255,255,0.9);
    line-height: 1.8;
    white-space: pre-wrap;
}

/* Fun travel facts ticker */
.ticker {
    background: rgba(240,147,251,0.1);
    border: 1px solid rgba(240,147,251,0.3);
    border-radius: 10px;
    padding: 0.7rem 1.5rem;
    color: #f093fb;
    font-size: 0.9rem;
    text-align: center;
    margin: 1rem 0;
}

/* Vibe tag pills */
.vibe-pill {
    display: inline-block;
    padding: 0.3rem 1rem;
    border-radius: 50px;
    font-size: 0.8rem;
    font-weight: 600;
    margin: 0.2rem;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #f093fb, #f5576c) !important;
    color: white !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 0.7rem 2rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 5px 20px rgba(240, 147, 251, 0.4) !important;
}

.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 10px 30px rgba(240, 147, 251, 0.6) !important;
}

/* Input fields */
.stTextInput > div > div > input,
.stNumberInput > div > div > input {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 12px !important;
    color: white !important;
    padding: 0.6rem 1rem !important;
}

/* Selectbox and slider */
.stSelectSlider > div,
.stRadio > div {
    background: transparent !important;
}

/* Expander */
.streamlit-expanderHeader {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 12px !important;
    color: white !important;
    font-weight: 600 !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e, #16213e) !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
}

/* Hide streamlit branding */
#MainMenu, footer, header { visibility: hidden; }

/* Success/warning/error */
.stSuccess {
    background: rgba(100,255,218,0.1) !important;
    border: 1px solid rgba(100,255,218,0.3) !important;
    border-radius: 12px !important;
}

.stWarning {
    background: rgba(255,183,77,0.1) !important;
    border: 1px solid rgba(255,183,77,0.3) !important;
    border-radius: 12px !important;
}

/* Spinner */
.stSpinner > div {
    border-top-color: #f093fb !important;
}

/* Divider */
hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.08) !important;
    margin: 1.5rem 0 !important;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0;">
        <div style="font-size:3rem;">🌍</div>
        <h2 style="color:white; margin:0; font-weight:800;">AI Travel</h2>
        <p style="color:rgba(255,255,255,0.4); font-size:0.8rem;">Planner v2.0 Pro</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style="color:rgba(255,255,255,0.7); font-size:0.85rem;">
    <b style="color:#f093fb;">🤖 AI Model:</b> Groq LLaMA3-70B<br><br>
    <b style="color:#f093fb;">🛠️ Tools:</b> 7 AI Tools<br><br>
    <b style="color:#f093fb;">📦 Data:</b> 6 JSON Datasets<br><br>
    <b style="color:#f093fb;">🌤️ Weather:</b> Open-Meteo API<br><br>
    <b style="color:#f093fb;">🚂 Transport:</b> Flights + Trains
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <p style="color:#4facfe; font-weight:600; font-size:0.9rem;">💡 Try These Trips</p>
    """, unsafe_allow_html=True)

    sample_trips = [
        "✈️ Delhi → Goa • 3 days",
        "🚂 Chennai → Coimbatore • 2 days",
        "🏔️ Mumbai → Manali • 5 days",
        "🏯 Bangalore → Jaipur • 4 days",
        "🌴 Delhi → Kerala • 6 days",
    ]
    for trip in sample_trips:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); border-radius:8px;
        padding:0.4rem 0.8rem; margin:0.3rem 0; color:rgba(255,255,255,0.7);
        font-size:0.8rem; border-left:2px solid #f093fb;">
        {trip}
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.history:
        st.markdown("---")
        st.markdown("""
        <p style="color:#4facfe; font-weight:600; font-size:0.9rem;">🕐 Recent Searches</p>
        """, unsafe_allow_html=True)
        for h in reversed(st.session_state.history[-3:]):
            st.markdown(f"""
            <div style="background:rgba(240,147,251,0.1); border-radius:8px;
            padding:0.4rem 0.8rem; margin:0.3rem 0; color:#f093fb;
            font-size:0.8rem;">🔍 {h}</div>
            """, unsafe_allow_html=True)

# ============================================================
# HERO BANNER
# ============================================================
st.markdown("""
<div class="hero">
    <div class="float-emoji">✈️</div>
    <h1>AI Travel Planner</h1>
    <p>Your personal AI travel expert — flights, hotels, weather & more</p>
    <span class="badge">🤖 Powered by LangChain + Groq LLaMA3-70B</span>
    &nbsp;
    <span class="badge">🆓 100% Free APIs</span>
    &nbsp;
    <span class="badge">⚡ Instant Planning</span>
</div>
""", unsafe_allow_html=True)

# Fun travel fact ticker
facts = [
    "🌍 Did you know? India has 40 UNESCO World Heritage Sites!",
    "🏖️ Goa has over 100 km of stunning coastline!",
    "🏔️ Manali sits at 2,050 meters above sea level!",
    "🐘 Kerala is home to 40% of India's elephant population!",
    "🕌 Agra's Taj Mahal took 22 years and 20,000 workers to build!",
]
import random
st.markdown(f"""
<div class="ticker">
    {random.choice(facts)}
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# TRANSPORT MODE + TRIP STYLE
# ============================================================
col_t, col_s = st.columns(2)

with col_t:
    st.markdown("<p style='color:rgba(255,255,255,0.8); font-weight:600;'>🚀 Transport Mode</p>", unsafe_allow_html=True)
    transport_mode = st.radio(
        "Transport",
        ["✈️ Flight", "🚂 Train", "🚌 Bus / Self Drive"],
        horizontal=True,
        label_visibility="collapsed"
    )

with col_s:
    st.markdown("<p style='color:rgba(255,255,255,0.8); font-weight:600;'>🎨 Trip Style</p>", unsafe_allow_html=True)
    trip_style = st.select_slider(
        "Style",
        options=["🎒 Budget", "⭐ Standard", "✨ Comfort", "💎 Premium", "👑 Luxury"],
        value="⭐ Standard",
        label_visibility="collapsed"
    )

st.markdown("---")

# ============================================================
# TRIP DETAILS FORM
# ============================================================
st.markdown("<h3 style='color:white; font-weight:700;'>📋 Trip Details</h3>", unsafe_allow_html=True)

with st.form("trip_form"):
    col1, col2 = st.columns(2)

    with col1:
        source = st.text_input("🛫 Travelling FROM", placeholder="e.g. Delhi")
        num_days = st.number_input("📅 Number of Days", min_value=1, max_value=14, value=3)
        budget = st.number_input("💰 Budget (INR)", min_value=1000, max_value=500000, value=20000, step=1000)

    with col2:
        destination = st.text_input("🛬 Travelling TO", placeholder="e.g. Goa")
        travel_date = st.date_input("📆 Travel Start Date", min_value=datetime.date.today())
        is_multi_city = st.checkbox("🌐 Multi-city trip?")

    if is_multi_city:
        stop2 = st.text_input("🛬 Stop 2 City", placeholder="e.g. Jaipur")
    else:
        stop2 = None

    submitted = st.form_submit_button("🚀 Plan My Dream Trip!", use_container_width=True)

# ============================================================
# PROCESS & DISPLAY RESULT
# ============================================================
if submitted:
    if not source or not destination:
        st.warning("⚠️ Please enter both source and destination cities!")
    elif is_multi_city and not stop2:
        st.warning("⚠️ Please enter your second stop city!")
    else:
        try:
            if is_multi_city:
                with st.spinner("🤖 AI is crafting your multi-city adventure..."):
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
                    f"Plan a {num_days} day {trip_style} style trip to {destination} "
                    f"from {source} starting {travel_date} with a budget of {budget} rupees. "
                    f"Preferred transport: {transport_mode}. "
                    f"Search for flights or trains, recommend a hotel, suggest top places to visit, "
                    f"check the weather, recommend restaurants, and give a full budget breakdown."
                )
                with st.spinner("🤖 Your AI travel expert is working on it..."):
                    result = run_travel_agent(query)
                st.session_state.history.append(f"{source} → {destination} ({num_days}d)")

            # SUCCESS HEADER
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(100,255,218,0.1),
            rgba(79,172,254,0.1)); border: 1px solid rgba(100,255,218,0.3);
            border-radius: 15px; padding: 1rem 1.5rem; text-align:center; margin: 1rem 0;">
            <h3 style="color:#64ffda; margin:0;">🎉 Your Dream Trip is Ready!</h3>
            <p style="color:rgba(255,255,255,0.6); margin:0.3rem 0 0;">
            Sit back, relax — your AI just planned your perfect vacation!</p>
            </div>
            """, unsafe_allow_html=True)

            # METRIC CARDS
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{num_days}</div>
                    <div class="metric-label">📅 Days</div>
                </div>""", unsafe_allow_html=True)
            with m2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">₹{budget:,}</div>
                    <div class="metric-label">💰 Budget</div>
                </div>""", unsafe_allow_html=True)
            with m3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{destination}</div>
                    <div class="metric-label">🏙️ Destination</div>
                </div>""", unsafe_allow_html=True)
            with m4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{trip_style.split()[1] if " " in trip_style else trip_style}</div>
                    <div class="metric-label">🎨 Style</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # ITINERARY EXPANDERS
            if is_multi_city and "LEG 1:" in result and "LEG 2:" in result:
                leg2_start = result.find("LEG 2:")
                leg1_content = result[:leg2_start]
                leg2_content = result[leg2_start:]
                with st.expander(f"✈️ Leg 1 — {source} → {destination}", expanded=True):
                    st.markdown(f'<div class="result-box">{leg1_content}</div>', unsafe_allow_html=True)
                with st.expander(f"✈️ Leg 2 — {destination} → {stop2}", expanded=True):
                    st.markdown(f'<div class="result-box">{leg2_content}</div>', unsafe_allow_html=True)
            else:
                with st.expander("✈️ Transport Details", expanded=True):
                    st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
                with st.expander("🏨 Hotel & Stay"):
                    st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
                with st.expander("🗺️ Day-wise Itinerary"):
                    st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
                with st.expander("🌤️ Weather Forecast"):
                    st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
                with st.expander("🍽️ Restaurant Picks"):
                    st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)
                with st.expander("💰 Budget Breakdown"):
                    st.markdown(f'<div class="result-box">{result}</div>', unsafe_allow_html=True)

            # --------------------------------------------------------
            # PDF EXPORT
            # --------------------------------------------------------
            st.markdown("---")
            st.markdown("<h4 style='color:white;'>📄 Download Your Itinerary</h4>", unsafe_allow_html=True)

            pdf_buffer = generate_trip_pdf(
                itinerary_text=result,
                source=source,
                destination=destination,
                num_days=num_days,
                travel_date=str(travel_date),
                budget=budget
            )

            st.download_button(
                label="📄 Download Itinerary as PDF",
                data=pdf_buffer,
                file_name="trip_itinerary.pdf",
                mime="application/pdf",
                use_container_width=True
            )

            # --------------------------------------------------------
            # SHARE BUTTONS
            # --------------------------------------------------------
            st.markdown("---")
            st.markdown("<h4 style='color:white;'>📤 Share Your Trip Plan</h4>", unsafe_allow_html=True)

            share_msg = f"🌍 My AI Travel Plan: {source} → {destination} for {num_days} days!\n\n{result[:400]}...\n\nPlanned by AI Travel Planner 🤖✈️"
            whatsapp_url = f"https://wa.me/?text={urllib.parse.quote(share_msg)}"

            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                st.link_button("📱 Share on WhatsApp", whatsapp_url, use_container_width=True)
            with sc2:
                st.code(result[:300] + "...", language=None)
            with sc3:
                if st.button("🔄 Plan Another Trip", use_container_width=True):
                    st.rerun()

            # RATING
            st.markdown("---")
            st.markdown("<h4 style='color:white;'>⭐ Rate Your AI Trip Plan</h4>", unsafe_allow_html=True)
            rating = st.feedback("stars")
            if rating is not None:
                stars = "⭐" * (rating + 1)
                st.success(f"{stars} Thanks for rating! Glad your trip is planned!")

            st.markdown("""
            <p style="color:rgba(255,255,255,0.3); font-size:0.75rem; text-align:center; margin-top:2rem;">
            ✨ Generated by AI Travel Planner — always verify prices and availability before booking.
            </p>
            """, unsafe_allow_html=True)

            st.balloons()

        except Exception as e:
            st.error(f"❌ Something went wrong. Please check your API key.\n\nError: {str(e)}")