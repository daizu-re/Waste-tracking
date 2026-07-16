from __future__ import annotations

from route_tracker.algorithms import compute_collection_strategies
from route_tracker.metrics import summarize_routes
from route_tracker.scenario import build_sample_city
from route_tracker.visualization import render_dashboard


def main() -> None:
    import streamlit as st

    st.set_page_config(
        page_title="Smart Waste Collection Route Optimization",
        page_icon="🗺️",
        layout="wide",
    )

    st.title("Smart Waste Collection Route Optimization")
    st.caption(
        "A graph-based simulation that compares route strategies for municipal waste collection on a real OpenStreetMap basemap."
    )

    city = build_sample_city()

    left, right = st.columns([1, 1])

    with left:
        st.subheader("City Map")
        depot_name = st.selectbox("Depot", options=list(city.nodes), index=0)
        only_active = st.checkbox("Highlight active bins only", value=True)

    with right:
        st.subheader("Operational Settings")
        fuel_rate = st.slider("Fuel consumption per km (liters)", 0.1, 0.5, 0.22, 0.01)
        speed = st.slider("Average truck speed (km/h)", 10, 50, 24, 1)
        fuel_cost = st.slider("Fuel cost per liter ($)", 1.0, 4.0, 2.5, 0.1)

    city.depot = depot_name
    strategies = compute_collection_strategies(city)
    summary = summarize_routes(strategies, fuel_rate, speed, fuel_cost)

    render_dashboard(
        city=city,
        strategies=strategies,
        summary=summary,
        depot_name=depot_name,
        only_active=only_active,
        fuel_rate=fuel_rate,
        speed_kmh=speed,
        fuel_cost_per_liter=fuel_cost,
    )


if __name__ == "__main__":
    main()
