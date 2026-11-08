# Courier Planning System — Project Report

## 1. Problem statement
A courier depot must decide which parcels fit into one vehicle, prioritize urgent parcels, and plan a low-distance visit sequence for the selected delivery locations. The integrated program combines sorting, optimization, graph processing, route planning, and runtime measurement.

## 2. Data model
Each parcel has an identifier, weight (kg), value score, deadline slot, priority score, and destination node. The road network is an undirected weighted graph. Vertices represent the depot/customer locations; edge weights represent road distance in kilometres.

## 3. Integrated workflow
`CSV input → Merge sort → 0/1 knapsack DP → destination extraction → Dijkstra shortest paths → nearest-neighbor TSP → benchmark and JSON output`

Sorting uses deadline ascending and priority descending for ties. Knapsack selects the subset with maximum total value under the vehicle capacity. Dijkstra supplies shortest-path distances for each route decision. The route heuristic selects the nearest unvisited delivery point and finally returns to the depot.

## 4. Algorithm analysis
| Component | Technique | Complexity |
|---|---|---|
| Parcel ordering | Merge sort | O(n log n) time |
| Box filling | 0/1 knapsack DP | O(nW) time and space |
| Single-source shortest path | Dijkstra + heap | O((V+E) log V) |
| Multi-stop routing | Nearest neighbor with Dijkstra legs | O(k(V+E) log V) approximately |
| Runtime comparison | `time.perf_counter` repeated trials | Depends on tested input sizes |

Here `n` is parcel count, `W` is integer vehicle capacity, `V` is graph vertices, `E` is graph edges, and `k` is the number of selected delivery points.

## 5. Correctness notes
- Merge sort combines sorted halves and preserves the defined comparison order.
- Knapsack recurrence compares excluding parcel `i` with including it when its weight fits. Backtracking reconstructs an optimal subset.
- Dijkstra is valid because all road weights are non-negative.
- Nearest-neighbor always chooses the smallest currently reachable shortest-path distance; it is a heuristic and may not produce the globally shortest tour.

## 6. Performance testing
Run `python benchmark.py` to generate two input scales, record the mean runtime of each component, and plot a comparison. The resulting chart and CSV are stored in `outputs/`. Runtime measurements vary by machine; interpret trends rather than treating a single run as universal.

## 7. Future improvements
1. Add deadline feasibility using estimated travel and service times.
2. Add directed roads, traffic-aware weights, and time-dependent edge costs.
3. Improve route quality with 2-opt or a vehicle-routing optimization library.
4. Reduce knapsack memory to O(W) using a one-dimensional DP array when the full table is not required for demonstration.
5. Use profiling and larger repeated trials; separate data loading from algorithm timing.

## 8. Execution evidence
The `screenshots/` folder contains a captured sample console run. The `outputs/` folder contains machine-readable results, the DP table, benchmark CSV, and runtime chart.
