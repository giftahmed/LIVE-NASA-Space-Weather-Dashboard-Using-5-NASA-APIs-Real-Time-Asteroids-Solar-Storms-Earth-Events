import streamlit as st
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================
# CONFIGURATION
# ============================================
st.set_page_config(
    page_title="NASA Space Weather Dashboard",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1e3a8a, #3b82f6, #60a5fa);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        text-align: center;
        color: #6b7280;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #334155;
    }
    .hazard-badge {
        background: #dc2626;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .safe-badge {
        background: #16a34a;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    .event-card {
        background: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.75rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        background: #1e293b;
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        color: #94a3b8;
    }
    .stTabs [aria-selected="true"] {
        background: #3b82f6 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

API_KEY = st.secrets.get("NASA_API_KEY", "DEMO_KEY")
BASE_URL = "https://api.nasa.gov"

# ============================================
# API FUNCTIONS
# ============================================

@st.cache_data(ttl=300)
def get_apod(date: Optional[str] = None) -> Dict:
    """Fetch Astronomy Picture of the Day."""
    url = f"{BASE_URL}/planetary/apod"
    params = {"api_key": API_KEY, "hd": "True"}
    if date:
        params["date"] = date
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"APOD Error: {e}")
        return {}

@st.cache_data(ttl=300)
def get_neo_feed(start_date: str, end_date: str) -> Dict:
    """Fetch Near Earth Objects."""
    url = f"{BASE_URL}/neo/rest/v1/feed"
    params = {
        "api_key": API_KEY,
        "start_date": start_date,
        "end_date": end_date
    }
    try:
        response = requests.get(url, params=params, timeout=20)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"NeoWs Error: {e}")
        return {}

@st.cache_data(ttl=300)
def get_donki_events(event_type: str = "CME", days: int = 30) -> List[Dict]:
    """Fetch space weather events from DONKI."""
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    end_date = datetime.now().strftime("%Y-%m-%d")
    url = f"{BASE_URL}/DONKI/{event_type}"
    params = {
        "api_key": API_KEY,
        "startDate": start_date,
        "endDate": end_date
    }
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"DONKI Error: {e}")
        return []

@st.cache_data(ttl=300)
def get_eonet_events(days: int = 7, category: Optional[str] = None) -> List[Dict]:
    """Fetch natural events from EONET."""
    url = "https://eonet.gsfc.nasa.gov/api/v3/events"
    params = {"days": days}
    if category:
        params["category"] = category
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json().get("events", [])
    except Exception as e:
        st.error(f"EONET Error: {e}")
        return []

@st.cache_data(ttl=300)
def get_epic_images(image_type: str = "natural") -> List[Dict]:
    """Fetch latest EPIC Earth images."""
    url = f"https://api.nasa.gov/EPIC/api/{image_type}"
    params = {"api_key": API_KEY}
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"EPIC Error: {e}")
        return []

@st.cache_data(ttl=300)
def get_mars_photos(rover: str = "curiosity", sol: int = 1000) -> List[Dict]:
    """Fetch Mars rover photos."""
    url = f"{BASE_URL}/mars-photos/api/v1/rovers/{rover}/photos"
    params = {"api_key": API_KEY, "sol": sol}
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json().get("photos", [])
    except Exception as e:
        st.error(f"Mars API Error: {e}")
        return []

# ============================================
# DATA PROCESSING
# ============================================

def process_neo_data(raw_data: Dict) -> pd.DataFrame:
    """Convert raw NEO data to DataFrame."""
    if not raw_data or "near_earth_objects" not in raw_data:
        return pd.DataFrame()

    records = []
    for date, neo_list in raw_data["near_earth_objects"].items():
        for neo in neo_list:
            est_diameter = neo.get("estimated_diameter", {}).get("kilometers", {})
            approach_data = neo.get("close_approach_data", [{}])[0]

            records.append({
                "date": date,
                "name": neo.get("name", "Unknown"),
                "id": str(neo.get("id", "")),
                "hazardous": neo.get("is_potentially_hazardous_asteroid", False),
                "diameter_min_km": est_diameter.get("estimated_diameter_min", 0),
                "diameter_max_km": est_diameter.get("estimated_diameter_max", 0),
                "velocity_kph": float(approach_data.get("relative_velocity", {}).get("kilometers_per_hour", 0)),
                "miss_distance_km": float(approach_data.get("miss_distance", {}).get("kilometers", 0)),
                "miss_distance_ld": float(approach_data.get("miss_distance", {}).get("lunar", 0)),
                "approach_date": approach_data.get("close_approach_date", "")
            })

    return pd.DataFrame(records)

def process_donki_cme(events: List[Dict]) -> pd.DataFrame:
    """Convert DONKI CME events to DataFrame."""
    records = []
    for event in events:
        analysis = event.get("cmeAnalyses", [{}])[0] if event.get("cmeAnalyses") else {}
        records.append({
            "time": event.get("startTime", ""),
            "activity_id": event.get("activityID", ""),
            "speed": analysis.get("speed", 0),
            "type": analysis.get("type", "Unknown"),
            "half_angle": analysis.get("halfAngle", 0),
            "linked_events": len(event.get("linkedEvents", []))
        })
    return pd.DataFrame(records)

def process_eonet_events(events: List[Dict]) -> pd.DataFrame:
    """Convert EONET events to DataFrame."""
    records = []
    for event in events:
        geometry = event.get("geometry", [{}])[0]
        coords = geometry.get("coordinates", [])
        categories = ", ".join(c.get("title", "") for c in event.get("categories", []))

        records.append({
            "title": event.get("title", "Unknown"),
            "category": categories,
            "date": geometry.get("date", ""),
            "longitude": coords[0] if len(coords) > 0 else None,
            "latitude": coords[1] if len(coords) > 1 else None,
            "id": event.get("id", "")
        })
    return pd.DataFrame(records)

def get_epic_image_url(image_data: Dict, image_type: str = "natural") -> str:
    """Construct EPIC image URL."""
    date = image_data.get("date", "").split(" ")[0].replace("-", "/")
    image_name = image_data.get("image", "")
    return f"https://epic.gsfc.nasa.gov/archive/{image_type}/{date}/png/{image_name}.png"

# ============================================
# UI COMPONENTS
# ============================================

def render_header():
    """Render the main header."""
    st.markdown('<h1 class="main-header">🚀 NASA Space Weather Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Real-time monitoring of asteroids, solar activity, Earth events & more</p>', unsafe_allow_html=True)

    # API Key warning
    if API_KEY == "DEMO_KEY":
        st.warning("⚠️ Using DEMO_KEY — rate limited to 30 req/hr. Get your free key at [api.nasa.gov](https://api.nasa.gov/)")

def render_sidebar():
    """Render sidebar controls."""
    with st.sidebar:
        st.header("⚙️ Controls")

        # Date range for NEO
        st.subheader("Asteroid Tracking")
        neo_days = st.slider("Days ahead", 1, 7, 7, key="neo_days")

        # DONKI settings
        st.subheader("Space Weather")
        donki_type = st.selectbox(
            "Event Type",
            ["CME", "GST", "FLR", "IPS", "SEP"],
            index=0
        )
        donki_days = st.slider("Lookback (days)", 7, 90, 30)

        # EONET settings
        st.subheader("Earth Events")
        eonet_days = st.slider("Event window (days)", 1, 30, 7)
        eonet_category = st.selectbox(
            "Category",
            ["All", "wildfires", "severeStorms", "volcanoes", "floods", "drought", "dustHaze"],
            index=0
        )

        # Mars settings
        st.subheader("Mars Rover")
        rover = st.selectbox("Rover", ["curiosity", "perseverance"])
        sol = st.number_input("Sol (Martian day)", 1, 4000, 1000)

        st.markdown("---")
        st.info("💡 Data refreshes every 5 minutes")

        return {
            "neo_days": neo_days,
            "donki_type": donki_type,
            "donki_days": donki_days,
            "eonet_days": eonet_days,
            "eonet_category": None if eonet_category == "All" else eonet_category,
            "rover": rover,
            "sol": sol
        }

def render_apod_section():
    """Render APOD section."""
    st.header("🌌 Astronomy Picture of the Day")

    apod_data = get_apod()
    if not apod_data:
        st.error("Failed to load APOD")
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        image_url = apod_data.get("hdurl") or apod_data.get("url", "")
        if apod_data.get("media_type") == "image":
            st.image(image_url, use_container_width=True)
        else:
            st.video(image_url)

    with col2:
        st.markdown(f"### {apod_data.get('title', 'Unknown')}")
        st.markdown(f"**Date:** {apod_data.get('date', 'N/A')}")
        if apod_data.get("copyright"):
            st.markdown(f"**©** {apod_data['copyright']}")

        with st.expander("📖 Explanation", expanded=True):
            st.write(apod_data.get("explanation", "No explanation available."))

        if apod_data.get("hdurl"):
            st.link_button("🔍 View HD Image", apod_data["hdurl"])

def render_neo_section(days: int):
    """Render Near Earth Objects section."""
    st.header("🪨 Near Earth Object Tracking")

    today = datetime.now().strftime("%Y-%m-%d")
    end = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")

    with st.spinner("Fetching asteroid data..."):
        raw_data = get_neo_feed(today, end)
        df = process_neo_data(raw_data)

    if df.empty:
        st.warning("No asteroid data available")
        return

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    total = len(df)
    hazardous = df["hazardous"].sum()
    closest = df["miss_distance_ld"].min()
    largest = df["diameter_max_km"].max()

    with col1:
        st.metric("Total Objects", total)
    with col2:
        st.metric("⚠️ Hazardous", int(hazardous), delta=f"{hazardous/total*100:.1f}%" if total > 0 else "0%")
    with col3:
        st.metric("Closest Approach", f"{closest:.1f} LD")
    with col4:
        st.metric("Largest Object", f"{largest:.2f} km")

    # Hazardous asteroids table
    if hazardous > 0:
        st.subheader("⚠️ Potentially Hazardous Asteroids")
        haz_df = df[df["hazardous"]].sort_values("miss_distance_ld")

        for _, row in haz_df.head(5).iterrows():
            with st.container():
                cols = st.columns([3, 2, 2, 2])
                with cols[0]:
                    st.markdown(f"**{row['name']}**")
                    st.caption(f"ID: {row['id']}")
                with cols[1]:
                    st.markdown(f"📏 {row['diameter_min_km']:.3f}-{row['diameter_max_km']:.3f} km")
                with cols[2]:
                    st.markdown(f"🌙 {row['miss_distance_ld']:.2f} LD")
                with cols[3]:
                    st.markdown(f"🚀 {float(row['velocity_kph']):,.0f} km/h")
                st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Size Distribution")
        fig = px.scatter(
            df, x="miss_distance_ld", y="diameter_max_km",
            color="hazardous", size="diameter_max_km",
            hover_data=["name", "velocity_kph"],
            color_discrete_map={True: "#dc2626", False: "#3b82f6"},
            labels={"miss_distance_ld": "Miss Distance (Lunar Distances)", 
                    "diameter_max_km": "Max Diameter (km)"}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Approach Timeline")
        timeline_df = df.groupby("date").agg({
            "name": "count",
            "hazardous": "sum"
        }).reset_index()
        timeline_df.columns = ["date", "total", "hazardous"]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=timeline_df["date"], y=timeline_df["total"],
            name="All Objects", marker_color="#3b82f6"
        ))
        fig.add_trace(go.Bar(
            x=timeline_df["date"], y=timeline_df["hazardous"],
            name="Hazardous", marker_color="#dc2626"
        ))
        fig.update_layout(barmode="group", height=400)
        st.plotly_chart(fig, use_container_width=True)

    # Full data table
    with st.expander("📊 View All Data"):
        st.dataframe(df.sort_values("miss_distance_ld"), use_container_width=True)

def render_donki_section(event_type: str, days: int):
    """Render DONKI space weather section."""
    st.header("🌞 Space Weather Events")

    with st.spinner(f"Fetching {event_type} events..."):
        events = get_donki_events(event_type, days)
        df = process_donki_cme(events) if event_type == "CME" else pd.DataFrame(events)

    if not events:
        st.info(f"No {event_type} events in the last {days} days")
        return

    st.metric(f"Total {event_type} Events", len(events))

    if event_type == "CME" and not df.empty:
        # CME speed chart
        fig = px.line(
            df.sort_values("time"),
            x="time", y="speed",
            title="CME Speed Over Time",
            labels={"speed": "Speed (km/s)", "time": "Date"},
            markers=True
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

        # Recent events
        st.subheader("Recent Events")
        for _, row in df.head(5).iterrows():
            with st.container():
                cols = st.columns([2, 2, 2, 1])
                with cols[0]:
                    st.markdown(f"**{row['activity_id'][:30]}...**")
                    st.caption(f"{row['time']}")
                with cols[1]:
                    st.markdown(f"⚡ {row['speed']} km/s")
                with cols[2]:
                    st.markdown(f"📐 {row['half_angle']}° half-angle")
                with cols[3]:
                    st.markdown(f"🔗 {row['linked_events']} linked")
                st.markdown("---")
    else:
        # Generic display for other event types
        for event in events[:5]:
            with st.expander(f"{event.get('activityID', 'Event')} — {event.get('startTime', 'N/A')}"):
                st.json(event)

def render_eonet_section(days: int, category: Optional[str]):
    """Render EONET natural events section."""
    st.header("🌍 Earth Natural Events")

    with st.spinner("Fetching natural events..."):
        events = get_eonet_events(days, category)
        df = process_eonet_events(events)

    if df.empty:
        st.info("No events found for selected criteria")
        return

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Events", len(df))
    with col2:
        categories = df["category"].nunique() if "category" in df.columns else 0
        st.metric("Categories", categories)
    with col3:
        st.metric("Time Window", f"{days} days")

    # Map
    if not df.empty and "latitude" in df.columns:
        st.subheader("Event Map")
        fig = px.scatter_geo(
            df, lat="latitude", lon="longitude",
            color="category", hover_name="title",
            projection="natural earth",
            title="Global Natural Events"
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

    # Event list
    st.subheader("Recent Events")
    for _, row in df.head(10).iterrows():
        with st.container():
            cols = st.columns([3, 2, 2])
            with cols[0]:
                st.markdown(f"**{row['title']}**")
            with cols[1]:
                st.markdown(f"🏷️ {row['category']}")
            with cols[2]:
                st.markdown(f"📅 {row['date'][:10]}")
            st.markdown("---")

def render_epic_section():
    """Render EPIC Earth images section."""
    st.header("🌎 Earth from Space (EPIC)")

    with st.spinner("Fetching latest Earth images..."):
        images = get_epic_images("natural")

    if not images:
        st.error("Failed to load EPIC images")
        return

    # Show latest image
    latest = images[0]
    image_url = get_epic_image_url(latest, "natural")

    col1, col2 = st.columns([2, 1])

    with col1:
        st.image(image_url, use_container_width=True, 
                 caption=f"Captured: {latest.get('date', 'N/A')}")

    with col2:
        st.subheader("Image Details")
        st.markdown(f"**Date:** {latest.get('date', 'N/A')}")

        centroid = latest.get("centroid_coordinates", {})
        if centroid:
            st.markdown(f"**Centroid:** Lat {centroid.get('lat', 'N/A'):.2f}, "
                       f"Lon {centroid.get('lon', 'N/A'):.2f}")

        dscovr = latest.get("dscovr_j2000_position", {})
        if dscovr:
            st.markdown(f"**DSCOVR Position:** X={dscovr.get('x', 'N/A'):.0f}, "
                       f"Y={dscovr.get('y', 'N/A'):.0f}, Z={dscovr.get('z', 'N/A'):.0f} km")

        st.link_button("🌐 View on EPIC Website", 
                      f"https://epic.gsfc.nasa.gov/image/{latest.get('image', '')}")

    # Gallery of recent images
    st.subheader("Recent Images")
    cols = st.columns(4)
    for i, img in enumerate(images[:8]):
        with cols[i % 4]:
            thumb_url = get_epic_image_url(img, "natural")
            st.image(thumb_url, caption=img.get("date", "")[:10], use_container_width=True)

def render_mars_section(rover: str, sol: int):
    """Render Mars rover photos section."""
    st.header(f"🔴 Mars Rover: {rover.title()}")

    with st.spinner(f"Fetching {rover} photos from Sol {sol}..."):
        photos = get_mars_photos(rover, sol)

    if not photos:
        st.warning(f"No photos found for {rover} on Sol {sol}")
        return

    st.metric("Photos Available", len(photos))

    # Camera filter
    cameras = list(set(p["camera"]["name"] for p in photos))
    selected_camera = st.selectbox("Filter by Camera", ["All"] + cameras)

    filtered = photos if selected_camera == "All" else [
        p for p in photos if p["camera"]["name"] == selected_camera
    ]

    # Photo gallery
    cols = st.columns(3)
    for i, photo in enumerate(filtered[:12]):
        with cols[i % 3]:
            st.image(photo["img_src"], 
                    caption=f"{photo['camera']['full_name']} — Sol {photo['sol']}",
                    use_container_width=True)

# ============================================
# MAIN APP
# ============================================

def main():
    render_header()
    settings = render_sidebar()

    # Create tabs
    tabs = st.tabs([
        "🌌 APOD", 
        "🪨 Asteroids", 
        "🌞 Space Weather", 
        "🌍 Earth Events", 
        "🌎 EPIC Earth", 
        "🔴 Mars Rover"
    ])

    with tabs[0]:
        render_apod_section()

    with tabs[1]:
        render_neo_section(settings["neo_days"])

    with tabs[2]:
        render_donki_section(settings["donki_type"], settings["donki_days"])

    with tabs[3]:
        render_eonet_section(settings["eonet_days"], settings["eonet_category"])

    with tabs[4]:
        render_epic_section()

    with tabs[5]:
        render_mars_section(settings["rover"], settings["sol"])

    # Footer
    st.markdown("---")
    st.markdown(
        "<p style='text-align: center; color: #6b7280;'>"
        "🚀 Built with NASA Open APIs | Data courtesy of NASA | "
        "<a href='https://api.nasa.gov/'>Get your API key</a>"
        "</p>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
