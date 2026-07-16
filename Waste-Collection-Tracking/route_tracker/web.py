from __future__ import annotations

from html import escape

from .algorithms import compute_collection_strategies
from .deploy import build_real_map_html
from .metrics import summarize_routes
from .scenario import build_sample_city


def build_homepage_html(
    depot_name: str = "Depot",
    only_active: bool = True,
    fuel_rate: float = 0.22,
    speed_kmh: float = 24.0,
    fuel_cost_per_liter: float = 2.5,
) -> str:
    city = build_sample_city()
    city.depot = depot_name if depot_name in city.nodes else city.depot
    strategies = compute_collection_strategies(city)
    summary = summarize_routes(strategies, fuel_rate, speed_kmh, fuel_cost_per_liter)

    map_html = build_real_map_html(city, strategies["Dijkstra"].path, city.depot, only_active)
    best_name = min(summary, key=lambda name: summary[name].distance_km)
    best = summary[best_name]

    rows = []
    for name, strategy in strategies.items():
        route_summary = summary[name]
        rows.append(
            "<tr>"
            f"<td>{escape(name)}</td>"
            f"<td>{strategy.distance_km:.2f}</td>"
            f"<td>{route_summary.fuel_liters:.2f}</td>"
            f"<td>{route_summary.fuel_cost:.2f}</td>"
            f"<td>{route_summary.estimated_time_hours:.2f}</td>"
            "</tr>"
        )

    return f"""
    <!doctype html>
    <html lang="en">
                <head>
                    <meta charset="utf-8" />
                    <meta name="viewport" content="width=device-width, initial-scale=1" />
                    <title>Smart Waste Collection Route Optimization</title>
                    <style>
                        :root {{
                            color-scheme: light;
                            --bg: #f4f7fb;
                            --panel: #ffffff;
                            --text: #0f172a;
                            --muted: #64748b;
                            --accent: #0f766e;
                            --border: #dbe3ee;
                        }}
                        body {{
                            margin: 0;
                            font-family: Arial, Helvetica, sans-serif;
                            background: radial-gradient(circle at top, #ffffff 0%, var(--bg) 45%, #e8eef7 100%);
                            color: var(--text);
                        }}
                        .wrap {{
                            max-width: 1240px;
                            margin: 0 auto;
                            padding: 32px 20px 48px;
                        }}
                        .hero {{
                            background: linear-gradient(135deg, #0f172a, #134e4a);
                            color: white;
                            border-radius: 24px;
                            padding: 28px;
                            box-shadow: 0 18px 40px rgba(15, 23, 42, 0.18);
                        }}
                        .hero h1 {{ margin: 0 0 8px; font-size: 34px; }}
                        .hero p {{ margin: 0; color: rgba(255,255,255,0.85); max-width: 760px; line-height: 1.5; }}
                        .grid {{
                            display: grid;
                            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                            gap: 14px;
                            margin: 18px 0 24px;
                        }}
                        .card {{
                            background: var(--panel);
                            border: 1px solid var(--border);
                            border-radius: 18px;
                            padding: 18px;
                            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
                        }}
                        .card .label {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.08em; }}
                        .card .value {{ font-size: 28px; font-weight: 700; margin-top: 8px; }}
                        .section {{
                            margin-top: 22px;
                            background: var(--panel);
                            border: 1px solid var(--border);
                            border-radius: 22px;
                            overflow: hidden;
                            box-shadow: 0 10px 28px rgba(15, 23, 42, 0.06);
                        }}
                        .section h2 {{ margin: 0; padding: 18px 20px; border-bottom: 1px solid var(--border); }}
                        .section .body {{ padding: 20px; }}
                        table {{ width: 100%; border-collapse: collapse; }}
                        th, td {{ text-align: left; padding: 12px 10px; border-bottom: 1px solid var(--border); }}
                        th {{ color: var(--muted); font-size: 13px; text-transform: uppercase; letter-spacing: 0.05em; }}
                        .map-frame {{ min-height: 720px; }}
                        .note {{ color: var(--muted); margin-top: 10px; font-size: 14px; }}
                    </style>
                </head>
                <body>
                    <div class="wrap">
                        <div class="hero">
                            <h1>Smart Waste Collection Route Optimization</h1>
                            <p>Vercel-compatible deployment view for the Kolkata route planner. Use the local Streamlit app for interactive controls; this page keeps the same graph logic and shows the optimized route on a real OpenStreetMap basemap.</p>
                        </div>

                        <div class="grid">
                            <div class="card"><div class="label">Best Route</div><div class="value">{escape(best_name)}</div></div>
                            <div class="card"><div class="label">Distance</div><div class="value">{best.distance_km:.2f} km</div></div>
                            <div class="card"><div class="label">Fuel</div><div class="value">{best.fuel_liters:.2f} L</div></div>
                            <div class="card"><div class="label">Cost</div><div class="value">${best.fuel_cost:.2f}</div></div>
                        </div>

                        <div class="section">
                            <h2>Real Map</h2>
                            <div class="body map-frame">{map_html}</div>
                        </div>

                        <div class="section">
                            <h2>Route Comparison</h2>
                            <div class="body">
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Algorithm</th><th>Distance (km)</th><th>Fuel (L)</th><th>Fuel Cost ($)</th><th>Time (h)</th>
                                        </tr>
                                    </thead>
                                    <tbody>{''.join(rows)}</tbody>
                                </table>
                                <div class="note">Tip: the Streamlit version includes sliders and toggles for deeper exploration. This page is the deployment-safe fallback for Vercel.</div>
                            </div>
                        </div>
                    </div>
                </body>
    </html>
    """