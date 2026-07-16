# Smart Waste Collection Route Optimization

An interactive route optimization demo for municipal waste collection. The app models a city as a weighted graph, compares BFS/DFS/Dijkstra/MST-based collection strategies, estimates operational cost, and visualizes optimized routes.

## Features

- Weighted city graph with road distances and coordinates
- Waste bin status tracking with active/inactive bins
- Route optimization using BFS, DFS, Dijkstra, and MST traversal
- Cost analysis with distance, fuel, and estimated time
- Real OpenStreetMap basemap with live route overlay
- Visual dashboard for map rendering and algorithm comparison

## Run

1. Install dependencies:

```bash
pip install -r requirements.txt
```

For the local Streamlit dashboard, install the full local set instead:

```bash
pip install -r requirements-local.txt
```

2. Start the app:

```bash
python run_local.py
```

## Vercel Deployment

The repository exports a Vercel-compatible FastAPI app from `api/index.py`. The root route is rewritten to that function through `vercel.json`, so a Vercel deploy serves the HTML dashboard at `/`. For local use, start the same FastAPI app with `python run_local.py`. If you want the richer local Streamlit interface, install `requirements-local.txt` and run `streamlit run app.py`.

## Project Structure

- `app.py` - Local Streamlit dashboard
- `run_local.py` - Stable local FastAPI launcher
- `api/index.py` - Vercel FastAPI entrypoint
- `vercel.json` - Root rewrite for the Vercel deployment
- `route_tracker/models.py` - Data models for nodes, bins, and city graphs
- `route_tracker/scenario.py` - Sample city map and waste bin layout
- `route_tracker/algorithms.py` - BFS, DFS, Dijkstra, and MST route logic
- `route_tracker/metrics.py` - Cost and performance calculations
- `route_tracker/visualization.py` - Graph and chart rendering helpers
- `docs/algorithm_comparison.md` - Complexity and algorithm comparison

The dashboard now includes a real map view rendered on top of OpenStreetMap, alongside the internal network graph view used by the optimizer.

## Notes

The app is designed as a reference implementation and can be extended to load real municipal GIS data, bin telemetry, or live traffic feeds.
