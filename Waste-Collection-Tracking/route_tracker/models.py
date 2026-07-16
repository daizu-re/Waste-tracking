from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import networkx as nx


@dataclass(frozen=True)
class CityNode:
    name: str
    x: float
    y: float


@dataclass(frozen=True)
class WasteBin:
    node: str
    fill_level: int
    active: bool


@dataclass
class CityMap:
    graph: nx.Graph = field(default_factory=nx.Graph)
    nodes: Dict[str, CityNode] = field(default_factory=dict)
    bins: Dict[str, WasteBin] = field(default_factory=dict)
    depot: str = "Depot"

    def active_bins(self) -> List[WasteBin]:
        return [waste_bin for waste_bin in self.bins.values() if waste_bin.active]

    def edge_distance(self, source: str, target: str) -> float:
        return float(self.graph[source][target]["distance"])

    def path_distance(self, path: List[str]) -> float:
        distance = 0.0
        for index in range(len(path) - 1):
            distance += self.edge_distance(path[index], path[index + 1])
        return distance

    def coordinates(self) -> Dict[str, Tuple[float, float]]:
        return {name: (node.x, node.y) for name, node in self.nodes.items()}
