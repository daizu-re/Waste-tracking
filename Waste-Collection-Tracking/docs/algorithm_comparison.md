# Algorithm Comparison Report

## Problem Context

The city is modeled as a weighted graph where intersections are nodes, roads are edges, and edge weights represent road distance. Waste bins have status flags that mark whether they must be collected on the current day.

## Algorithms

### BFS
- Explores the graph level by level.
- Good for reachability checks and baseline traversal order.
- Not distance aware, so it usually produces longer collection routes.
- Time complexity: `O(V + E)`.

### DFS
- Explores one branch deeply before backtracking.
- Good for simple traversal and connectivity exploration.
- Also not distance aware, so it can create inefficient collection paths.
- Time complexity: `O(V + E)`.

### Dijkstra
- Computes shortest road paths using edge weights.
- Best fit for route optimization when road distance matters.
- In this project it is used to connect the depot and active bins through the shortest available road segments.
- Time complexity: `O((V + E) log V)` with a priority queue.

### MST
- Connects all required stops with minimum total edge weight.
- Useful as a low-cost coverage backbone for collection planning.
- Does not directly produce an ordered truck route, so it is converted into a traversal path.
- Time complexity: `O(E log V)` for Prim/Kruskal implementations.

## Practical Comparison

| Algorithm | Main Strength | Main Weakness | Route Quality |
| --- | --- | --- | --- |
| BFS | Simple traversal | Ignores distance | Low |
| DFS | Simple traversal | Can backtrack heavily | Low |
| Dijkstra | Shortest weighted paths | More expensive than BFS/DFS | High |
| MST | Minimum coverage tree | Needs traversal conversion | Medium-High |

## System Complexity

Let `V` be the number of city nodes and `E` the number of roads.

- Graph construction: `O(V + E)`
- BFS traversal route: `O(V + E)`
- DFS traversal route: `O(V + E)`
- Dijkstra-based collection route: `O(k (E log V))` for `k` active bin stops
- MST route: `O(E log V)` plus traversal conversion

## Notes

The reference implementation is designed for a static demo city. For deployment, the system can be extended with live road data, daily waste forecasts, and truck capacity constraints.
