from __future__ import annotations

import math
from typing import Iterable, Tuple

import networkx as nx

from .models import CityMap, CityNode, WasteBin


NODE_LAYOUT = {
    "Depot": (88.3649, 22.5726),
    "BBD Bagh": (88.3472, 22.5720),
    "Park Street": (88.3628, 22.5490),
    "Esplanade": (88.3489, 22.5567),
    "Salt Lake": (88.4167, 22.5849),
    "Ballygunge": (88.3672, 22.5287),
    "Howrah": (88.3303, 22.5958),
    "New Town": (88.4733, 22.5754),
    "Gariahat": (88.3703, 22.5180),
    "Jadavpur": (88.3698, 22.4950),
}

EDGE_LIST: Iterable[Tuple[str, str]] = [
    ("Depot", "BBD Bagh"),
    ("Depot", "Esplanade"),
    ("BBD Bagh", "Howrah"),
    ("BBD Bagh", "Park Street"),
    ("Park Street", "Ballygunge"),
    ("Park Street", "Gariahat"),
    ("Esplanade", "Salt Lake"),
    ("Esplanade", "Park Street"),
    ("Salt Lake", "New Town"),
    ("Salt Lake", "Howrah"),
    ("Ballygunge", "Jadavpur"),
    ("Ballygunge", "Gariahat"),
    ("Howrah", "Esplanade"),
    ("New Town", "BBD Bagh"),
    ("Gariahat", "Jadavpur"),
    ("Park Street", "Howrah"),
    ("Salt Lake", "Park Street"),
]

BIN_STATUS = {
    "BBD Bagh": (74, True),
    "Park Street": (28, False),
    "Esplanade": (81, True),
    "Salt Lake": (57, True),
    "Ballygunge": (45, False),
    "Howrah": (91, True),
    "New Town": (33, False),
    "Gariahat": (69, True),
    "Jadavpur": (22, False),
}


def _road_distance_km(first: tuple[float, float], second: tuple[float, float]) -> float:
    first_lon, first_lat = first
    second_lon, second_lat = second
    radius_km = 6371.0
    delta_lat = math.radians(second_lat - first_lat)
    delta_lon = math.radians(second_lon - first_lon)
    lat1 = math.radians(first_lat)
    lat2 = math.radians(second_lat)

    a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(delta_lon / 2) ** 2
    return 1.25 * radius_km * (2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)))


def build_sample_city() -> CityMap:
    graph = nx.Graph()
    nodes = {}
    bins = {}

    for name, (x, y) in NODE_LAYOUT.items():
        graph.add_node(name, x=x, y=y)
        nodes[name] = CityNode(name=name, x=x, y=y)

    for source, target in EDGE_LIST:
        graph.add_edge(source, target, distance=round(_road_distance_km(NODE_LAYOUT[source], NODE_LAYOUT[target]), 2))

    for node, (fill_level, active) in BIN_STATUS.items():
        bins[node] = WasteBin(node=node, fill_level=fill_level, active=active)

    return CityMap(graph=graph, nodes=nodes, bins=bins, depot="Depot")
