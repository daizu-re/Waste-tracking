from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .algorithms import RouteStrategy
from .models import CityMap


@dataclass(frozen=True)
class RouteSummary:
    distance_km: float
    fuel_liters: float
    fuel_cost: float
    estimated_time_hours: float


def summarize_route(distance_km: float, fuel_rate: float, speed_kmh: float, fuel_cost_per_liter: float) -> RouteSummary:
    fuel_liters = distance_km * fuel_rate
    fuel_cost = fuel_liters * fuel_cost_per_liter
    estimated_time_hours = distance_km / speed_kmh if speed_kmh else 0.0
    return RouteSummary(
        distance_km=distance_km,
        fuel_liters=fuel_liters,
        fuel_cost=fuel_cost,
        estimated_time_hours=estimated_time_hours,
    )


def summarize_routes(
    strategies: Dict[str, RouteStrategy],
    fuel_rate: float,
    speed_kmh: float,
    fuel_cost_per_liter: float,
) -> Dict[str, RouteSummary]:
    return {
        name: summarize_route(
            distance_km=strategy.distance_km,
            fuel_rate=fuel_rate,
            speed_kmh=speed_kmh,
            fuel_cost_per_liter=fuel_cost_per_liter,
        )
        for name, strategy in strategies.items()
    }
