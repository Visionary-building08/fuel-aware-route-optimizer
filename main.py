"""
Streamlit UI for Fuel-Aware Route Optimizer.
Uses free OpenStreetMap + OSRM APIs : no API key needed.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from core.route_optimizer import RouteOptimizer
from utils.helpers import format_duration, validate_inputs

st.set_page_config(page_title="Fuel-Aware Route Optimizer", page_icon="⛽", layout="centered")

# ✅ SESSION STATE INIT (ADDED)
if "result" not in st.session_state:
    st.session_state.result = None

st.title("⛽ Fuel-Aware Route Optimizer")
st.caption("Optimizes your Trivandrum route using real road distances : no API key needed.")
st.divider()

with st.sidebar:
    st.header("ℹ️ Info")
    st.success("✅ No API key required!\nUsing free OpenStreetMap + OSRM.")
    st.markdown("---")
    st.markdown(
        "**Road quality** and **traffic** penalties are auto-applied "
        "based on your time and destination area."
    )

col1, col2 = st.columns(2)
with col1:
    start_location = st.text_input("📍 Start Location", placeholder="e.g. Technopark, Trivandrum")
    time_of_day = st.selectbox("🕐 Time of Travel", ["morning", "afternoon", "evening"],
                                format_func=str.capitalize)
with col2:
    mileage = st.number_input("🚗 Vehicle Mileage (km/l)", min_value=1.0, max_value=100.0,
                               value=15.0, step=0.5)
    num_stops = st.slider("Number of Stops", min_value=1, max_value=6, value=3)

st.subheader("📌 Stops")
stops = []
cols = st.columns(2)
for i in range(num_stops):
    with cols[i % 2]:
        stops.append(st.text_input(f"Stop {i+1}", placeholder="e.g. Kovalam", key=f"stop_{i}"))

st.divider()

if st.button("🗺️ Optimize Route", use_container_width=True, type="primary"):
    errors = validate_inputs(start_location, stops, mileage)
    if errors:
        for e in errors:
            st.error(e)
        st.stop()

    clean_stops = [s.strip() for s in stops if s.strip()]

    with st.spinner("Geocoding locations and fetching real road data... (may take ~20 seconds)"):
        try:
            optimizer = RouteOptimizer()
            # ✅ SAVE RESULT IN SESSION STATE (CHANGED)
            st.session_state.result = optimizer.optimize(
                start=start_location.strip(),
                stops=clean_stops,
                time_of_day=time_of_day,
                mileage_kmpl=mileage,
            )
        except ValueError as ve:
            st.error(str(ve))
            st.stop()
        except Exception as ex:
            st.error(f"Unexpected error: {ex}")
            st.stop()

# ✅ DISPLAY RESULT OUTSIDE BUTTON (ADDED BLOCK)
if st.session_state.result:
    result = st.session_state.result

    st.success("Route optimized!")
    st.subheader("📊 Summary")
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Distance", f"{result['total_distance_km']} km")
    m2.metric("Est. Time", format_duration(result["total_duration_min"]))
    m3.metric("Fuel Cost", f"₹{result['total_fuel_cost_inr']}")
    st.columns([1,2])[0].metric("Fuel Used", f"{result['total_fuel_litres']} L")

    st.subheader("🛣️ Optimized Route")
    st.info("**" + " → ".join(result["ordered_route"]) + "**")

    # Map using folium
    try:
        import folium
        from streamlit_folium import st_folium

        coords = result["ordered_coords"]
        m = folium.Map(location=coords[0], zoom_start=12)
        for idx, (loc, coord) in enumerate(zip(result["ordered_route"], coords)):
            folium.Marker(
                coord,
                popup=loc,
                tooltip=f"{idx+1}. {loc}",
                icon=folium.Icon(color="red" if idx == 0 else "blue", icon="info-sign"),
            ).add_to(m)
        folium.PolyLine(coords, color="blue", weight=3, opacity=0.7).add_to(m)
        st.subheader("🗺️ Route Map")
        st_folium(m, width=700, height=400)
    except ImportError:
        st.info("💡 Install `folium` and `streamlit-folium` to see the route on a map.")

    st.subheader("📋 Segment Breakdown")
    for seg in result["segments"]:
        with st.expander(f"{seg['from']}  →  {seg['to']}"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Distance", f"{seg['distance_km']} km")
            c2.metric("Duration", f"{seg['duration_min']} min")
            c3.metric("Fuel Cost", f"₹{seg['adjusted_cost']}")

    st.divider()
    st.caption("ℹ️ Traffic penalty (+25%) applied for morning/evening. Road quality penalties applied per area.")