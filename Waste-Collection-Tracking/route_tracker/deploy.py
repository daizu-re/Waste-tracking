from __future__ import annotations

import folium

from .models import CityMap


def build_real_map_html(city: CityMap, route: list[str], depot_name: str, only_active: bool) -> str:
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