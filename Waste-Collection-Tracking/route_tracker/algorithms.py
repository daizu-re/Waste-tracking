from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Tuple

import networkx as nx

from .models import CityMap


@dataclass(frozen=True)
class RouteStrategy:
    name: str
    path: List[str]
    distance_km: float


def _nearest_active_bin(city: CityMap, current: str, remaining: set[str]) -> str:
    return min(remaining, key=lambda node: nx.shortest_path_length(city.graph, current, node, weight="distance"))


def dijkstra_collection_route(city: CityMap) -> List[str]:
    active = {waste_bin.node for waste_bin in city.active_bins()}
    if not active:
        return [city.depot]

    route = [city.depot]
    current = city.depot
    remaining = set(active)

    while remaining:
        next_bin = _nearest_active_bin(city, current, remaining)
        segment = nx.shortest_path(city.graph, current, next_bin, weight="distance")
        route.extend(segment[1:])
        current = next_bin
        remaining.remove(next_bin)

    return route


def _traversal_route(city: CityMap, mode: str) -> List[str]:
    active = {waste_bin.node for waste_bin in city.active_bins()}
    visited = {city.depot}
    order = [city.depot]

    if mode == "bfs":
        frontier = deque([city.depot])
        pop = frontier.popleft
        push = frontier.append
    else:
        frontier = [city.depot]
        pop = frontier.pop

        def push(value: str) -> None:
            frontier.append(value)

    while frontier:
        current = pop()
        neighbors = sorted(city.graph.neighbors(current))
        if mode == "dfs":
            neighbors = list(reversed(neighbors))
        for neighbor in neighbors:
            if neighbor in visited:
                continue
            visited.add(neighbor)
            push(neighbor)
            if neighbor in active:
                order.append(neighbor)

    if order[-1] != city.depot:
        order.append(city.depot)
    return _route_via_shortest_hops(city, order)


def _route_via_shortest_hops(city: CityMap, stops: List[str]) -> List[str]:
    if len(stops) < 2:
        return stops

    route = [stops[0]]
    for index in range(len(stops) - 1):
        segment = nx.shortest_path(city.graph, stops[index], stops[index + 1], weight="distance")
        route.extend(segment[1:])
    return route


def mst_collection_route(city: CityMap) -> List[str]:
    active = [waste_bin.node for waste_bin in city.active_bins()]
    required_nodes = [city.depot, *active]
    subgraph = city.graph.subgraph(required_nodes).copy()
    tree = nx.minimum_spanning_tree(subgraph, weight="distance")
    order = list(nx.dfs_preorder_nodes(tree, source=city.depot))
    return _route_via_shortest_hops(city, order)


def compute_collection_strategies(city: CityMap) -> Dict[str, RouteStrategy]:
    strategies = {
        "BFS": RouteStrategy("BFS", _traversal_route(city, "bfs"), 0.0),
        "DFS": RouteStrategy("DFS", _traversal_route(city, "dfs"), 0.0),
        "Dijkstra": RouteStrategy("Dijkstra", dijkstra_collection_route(city), 0.0),
        "MST": RouteStrategy("MST", mst_collection_route(city), 0.0),
    }

    return {
        name: RouteStrategy(name=value.name, path=value.path, distance_km=city.path_distance(value.path))
        for name, value in strategies.items()
    }
