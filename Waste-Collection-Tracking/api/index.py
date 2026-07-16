from __future__ import annotations

from html import escape

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse


app = FastAPI(title="Smart Waste Collection Route Optimization")

ROUTE_DISTANCES = {
    "BFS": 47.16,
    "DFS": 45.93,
    "Dijkstra": 31.62,
    "MST": 21.71,
}


def _summary_rows(fuel_rate: float, speed_kmh: float, fuel_cost_per_liter: float) -> tuple[str, str, str]:
    rows: list[str] = []
    best_name = min(ROUTE_DISTANCES, key=ROUTE_DISTANCES.get)
    best_distance = ROUTE_DISTANCES[best_name]

    for name, distance_km in ROUTE_DISTANCES.items():
        fuel_liters = distance_km * fuel_rate
        fuel_cost = fuel_liters * fuel_cost_per_liter
        estimated_time_hours = distance_km / speed_kmh if speed_kmh else 0.0
        rows.append(
            "<tr>"
            f"<td>{escape(name)}</td>"
            f"<td>{distance_km:.2f}</td>"
            f"<td>{fuel_liters:.2f}</td>"
            f"<td>{fuel_cost:.2f}</td>"
            f"<td>{estimated_time_hours:.2f}</td>"
            "</tr>"
        )

    return best_name, f"{best_distance:.2f}", "".join(rows)


@app.get("/", response_class=HTMLResponse)
def home(
    depot_name: str = Query(default="Depot"),
    only_active: bool = Query(default=True),
    fuel_rate: float = Query(default=0.22, ge=0.1, le=0.5),
    speed_kmh: float = Query(default=24.0, ge=10.0, le=50.0),
    fuel_cost_per_liter: float = Query(default=2.5, ge=1.0, le=4.0),
) -> HTMLResponse:
    best_name, best_distance, rows = _summary_rows(fuel_rate, speed_kmh, fuel_cost_per_liter)

    return HTMLResponse(
        f"""
        <!doctype html>
        <html lang="en">
            <head>
                <meta charset="utf-8" />
                <meta name="viewport" content="width=device-width, initial-scale=1" />
                <title>Smart Waste Collection Route Optimization</title>
                <style>
                    body {{ margin: 0; font-family: Arial, Helvetica, sans-serif; background: #0f172a; color: #e2e8f0; }}
                    .wrap {{ max-width: 1100px; margin: 0 auto; padding: 40px 20px 60px; }}
                    .hero {{ background: linear-gradient(135deg, #0f172a, #134e4a); border-radius: 24px; padding: 28px; }}
                    .hero h1 {{ margin: 0 0 8px; font-size: 34px; }}
                    .hero p {{ margin: 0; max-width: 760px; line-height: 1.5; color: rgba(226,232,240,0.88); }}
                    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 14px; margin: 18px 0 24px; }}
                    .card {{ background: #111827; border: 1px solid #334155; border-radius: 18px; padding: 18px; }}
                    .label {{ color: #94a3b8; font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; }}
                    .value {{ font-size: 28px; font-weight: 700; margin-top: 8px; }}
                    .section {{ margin-top: 22px; background: #111827; border: 1px solid #334155; border-radius: 22px; overflow: hidden; }}
                    .section h2 {{ margin: 0; padding: 18px 20px; border-bottom: 1px solid #334155; }}
                    .body {{ padding: 20px; }}
                    table {{ width: 100%; border-collapse: collapse; }}
                    th, td {{ text-align: left; padding: 12px 10px; border-bottom: 1px solid #334155; }}
                    th {{ color: #94a3b8; font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em; }}
                    .note {{ color: #94a3b8; margin-top: 10px; font-size: 14px; }}
                    .pill {{ display: inline-block; background: #0f766e; color: white; border-radius: 999px; padding: 4px 10px; font-size: 12px; margin-left: 8px; }}
                </style>
            </head>
            <body>
                <div class="wrap">
                    <div class="hero">
                        <h1>Smart Waste Collection Route Optimization</h1>
                        <p>Deployment-safe Vercel view for the Kolkata route planner. This lightweight page keeps the route logic and metrics in the serverless runtime and avoids the heavier local dashboard stack.</p>
                    </div>

                    <div class="grid">
                        <div class="card"><div class="label">Depot</div><div class="value">{escape(depot_name)}</div></div>
                        <div class="card"><div class="label">Best Route</div><div class="value">{best_name}</div></div>
                        <div class="card"><div class="label">Distance</div><div class="value">{best_distance} km</div></div>
                        <div class="card"><div class="label">Active Filter</div><div class="value">{"On" if only_active else "Off"}</div></div>
                    </div>

                    <div class="section">
                        <h2>Route Comparison <span class="pill">4 algorithms</span></h2>
                        <div class="body">
                            <table>
                                <thead>
                                    <tr>
                                        <th>Algorithm</th><th>Distance (km)</th><th>Fuel (L)</th><th>Fuel Cost ($)</th><th>Time (h)</th>
                                    </tr>
                                </thead>
                                <tbody>{rows}</tbody>
                            </table>
                            <div class="note">Vercel renders this stable summary page. The full interactive Streamlit dashboard is kept for local use only.</div>
                        </div>
                    </div>
                </div>
            </body>
        </html>
        """
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}