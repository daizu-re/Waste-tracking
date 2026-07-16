from __future__ import annotations

from typing import Dict

import folium
import plotly.graph_objects as go
import streamlit.components.v1 as components
import streamlit as st

from .algorithms import RouteStrategy
from .metrics import RouteSummary
from .models import CityMap


def render_dashboard(
    city: CityMap,
    strategies: Dict[str, RouteStrategy],
    summary: Dict[str, RouteSummary],
    depot_name: str,
    only_active: bool,
    fuel_rate: float,
    speed_kmh: float,
    fuel_cost_per_liter: float,
) -> None:
    tabs = st.tabs(["Real Map", "Network View", "Route Comparison", "Cost Analysis", "Algorithm Notes"])

    with tabs[0]:
        components.html(
            _build_real_map(city, strategies["Dijkstra"].path, depot_name, only_active),
            height=720,
            scrolling=False,
        )
        st.write("OpenStreetMap basemap with active bins highlighted and the optimized Dijkstra route in red.")

    with tabs[1]:
        st.plotly_chart(
            _build_city_figure(city, strategies["Dijkstra"].path, depot_name, only_active),
            use_container_width=True,
        )
        st.write("Internal graph layout used by the optimization engine.")

    with tabs[2]:
        comparison_rows = []
        for name, strategy in strategies.items():
            route_summary = summarize_with_settings(strategy.distance_km, fuel_rate, speed_kmh, fuel_cost_per_liter)
            comparison_rows.append(
                {
                    "Algorithm": name,
                    "Distance (km)": round(route_summary.distance_km, 2),
                    "Fuel (L)": round(route_summary.fuel_liters, 2),
                    "Fuel Cost ($)": round(route_summary.fuel_cost, 2),
                    "Time (h)": round(route_summary.estimated_time_hours, 2),
                }
            )
        st.dataframe(comparison_rows, use_container_width=True, hide_index=True)

    with tabs[3]:
        best_name = min(summary, key=lambda name: summary[name].distance_km)
        best = summary[best_name]
        st.metric("Best route", best_name)
        cols = st.columns(3)
        cols[0].metric("Distance", f"{best.distance_km:.2f} km")
        cols[1].metric("Fuel", f"{best.fuel_liters:.2f} L")
        cols[2].metric("Fuel cost", f"${best.fuel_cost:.2f}")

        comparison_figure = go.Figure()
        for metric_name, color in [("Distance", "#0f766e"), ("Fuel", "#dc2626"), ("Cost", "#f59e0b")]:
            comparison_figure.add_trace(
                go.Bar(
                    x=list(summary.keys()),
                    y=[
                        route_summary.distance_km
                        if metric_name == "Distance"
                        else route_summary.fuel_liters
                        if metric_name == "Fuel"
                        else route_summary.fuel_cost
                        for route_summary in summary.values()
                    ],
                    name=metric_name,
                    marker_color=color,
                )
            )
        comparison_figure.update_layout(
            barmode="group",
            margin=dict(l=10, r=10, t=20, b=10),
            yaxis_title="Value",
            plot_bgcolor="#f8fafc",
            paper_bgcolor="#f8fafc",
            height=420,
        )
        st.plotly_chart(comparison_figure, use_container_width=True)

    with tabs[4]:
        st.markdown(
            """
            - **BFS / DFS**: explore the city graph in traversal order; useful as baselines, but not distance optimal.
            - **Dijkstra**: finds shortest road paths between collection stops and gives the most practical optimized route.
            - **MST**: connects all required bins with minimum total edge weight, which is useful for reducing coverage cost.
            """
        )


def summarize_with_settings(distance_km: float, fuel_rate: float, speed_kmh: float, fuel_cost_per_liter: float) -> RouteSummary:
    return RouteSummary(
        distance_km=distance_km,
        fuel_liters=distance_km * fuel_rate,
        fuel_cost=distance_km * fuel_rate * fuel_cost_per_liter,
        estimated_time_hours=distance_km / speed_kmh if speed_kmh else 0.0,
    )


def build_real_map_html(city: CityMap, route: list[str], depot_name: str, only_active: bool) -> str:
    return _build_real_map(city, route, depot_name, only_active)


def _build_real_map(city: CityMap, route: list[str], depot_name: str, only_active: bool) -> str:
    coordinates = city.coordinates()
    depot_lat = coordinates[depot_name][1]
    depot_lon = coordinates[depot_name][0]
    map_object = folium.Map(location=[depot_lat, depot_lon], zoom_start=14, tiles="OpenStreetMap")

    for source, target, data in city.graph.edges(data=True):
        first_lon, first_lat = coordinates[source]
        second_lon, second_lat = coordinates[target]
        folium.PolyLine(
            locations=[[first_lat, first_lon], [second_lat, second_lon]],
            color="#cbd5e1",
            weight=3,
            opacity=0.8,
            tooltip=f"Road: {source} to {target} ({data['distance']:.2f} km)",
        ).add_to(map_object)

    route_points = []
    for node_name in route:
        lon, lat = coordinates[node_name]
        route_points.append([lat, lon])
    if len(route_points) > 1:
        folium.PolyLine(
            locations=route_points,
            color="#dc2626",
            weight=6,
            opacity=0.95,
            tooltip="Optimized route",
        ).add_to(map_object)

    for name, node in city.nodes.items():
        if only_active and name not in city.bins and name != depot_name:
            continue
        lon, lat = node.x, node.y
        if name == depot_name:
            color = "#0f766e"
            radius = 10
            label = f"Depot: {name}"
        elif name in city.bins:
            waste_bin = city.bins[name]
            color = "#ef4444" if waste_bin.active else "#f59e0b"
            radius = 8 if waste_bin.active else 6
            label = f"{name} | Fill {waste_bin.fill_level}% | {'Active' if waste_bin.active else 'Idle'}"
        else:
            color = "#64748b"
            radius = 5
            label = name

        folium.CircleMarker(
            location=[lat, lon],
            radius=radius,
            color="#111827",
            weight=1,
            fill=True,
            fill_color=color,
            fill_opacity=0.95,
            tooltip=label,
            popup=label,
        ).add_to(map_object)

    return map_object._repr_html_()


def _build_city_figure(city: CityMap, route: list[str], depot_name: str, only_active: bool) -> go.Figure:
    coords = city.coordinates()

    edge_x = []
    edge_y = []
    for source, target, data in city.graph.edges(data=True):
        x0, y0 = coords[source]
        x1, y1 = coords[target]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    route_x = []
    route_y = []
    for index in range(len(route) - 1):
        source = route[index]
        target = route[index + 1]
        x0, y0 = coords[source]
        x1, y1 = coords[target]
        route_x.extend([x0, x1, None])
        route_y.extend([y0, y1, None])

    node_x = []
    node_y = []
    node_text = []
    node_size = []
    node_color = []

    for name, node in city.nodes.items():
        if only_active and name not in city.bins and name != depot_name:
            continue
        node_x.append(node.x)
        node_y.append(node.y)
        if name in city.bins:
            waste_bin = city.bins[name]
            node_text.append(f"{name}<br>Fill: {waste_bin.fill_level}%<br>Status: {'Active' if waste_bin.active else 'Idle'}")
            node_size.append(18 if waste_bin.active else 12)
            node_color.append("#ef4444" if waste_bin.active else "#fbbf24")
        else:
            node_text.append(f"{name}<br>Depot")
            node_size.append(22)
            node_color.append("#0f766e")

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=edge_x,
            y=edge_y,
            mode="lines",
            line=dict(color="#94a3b8", width=2),
            hoverinfo="none",
            name="Road network",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=route_x,
            y=route_y,
            mode="lines",
            line=dict(color="#dc2626", width=5),
            hoverinfo="none",
            name="Optimized route",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=node_x,
            y=node_y,
            mode="markers+text",
            text=[name for name in city.nodes if not only_active or name in city.bins or name == depot_name],
            textposition="top center",
            hovertext=node_text,
            hoverinfo="text",
            marker=dict(size=node_size, color=node_color, line=dict(width=1, color="#111827")),
            name="Nodes",
        )
    )
    fig.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
        plot_bgcolor="#f8fafc",
        paper_bgcolor="#f8fafc",
        height=650,
    )
    return fig
