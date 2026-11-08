# Integrated Courier Planning System

A Python project combining four algorithmic components in one workflow:

1. **Parcel prioritization — Merge sort:** stable `O(n log n)` ordering by earliest deadline, then higher priority.
2. **Box filling — 0/1 Knapsack (dynamic programming):** maximizes parcel value without exceeding vehicle capacity. Time `O(nW)`, space `O(nW)`.
3. **Individual shortest paths — Dijkstra:** computes shortest road distances from a node using a min-priority queue. With adjacency lists and a binary heap: `O((V+E) log V)`.
4. **Multi-stop route — nearest-neighbor TSP approximation:** repeatedly visits the closest unvisited delivery point, where closeness is measured using Dijkstra distance. It returns to the depot when reachable. This is a heuristic, not a guaranteed optimal TSP solution.

## Requirements
- Python 3.9+
- `matplotlib` only for chart generation; the application itself uses the Python standard library.

## Run
From this directory:

```bash
python main.py
```

Custom capacity and input data directory:

```bash
python main.py --capacity 25 --data data --start DEPOT
```

The program writes `outputs/result.json` and `outputs/dp_table.json`.

## Dataset format
- `data/parcels.csv`: `id,weight,value,deadline,priority,destination`
- `data/roads.csv`: undirected road edges as `from,to,distance`

All distances and parcel weights are illustrative. Deadlines are integer time slots (smaller means sooner); value is the benefit score used by knapsack; priority is a tie-breaker.

## Benchmark and chart
Run `python benchmark.py`. It generates small and large synthetic parcel/road datasets, records average component runtimes in `outputs/benchmark.csv`, and creates `outputs/runtime_comparison.png`. Timings depend on hardware and Python version.

## Project structure
```text
courier_planner/
├── main.py
├── benchmark.py
├── README.md
├── REPORT.md
├── requirements.txt
├── data/
│   ├── parcels.csv
│   └── roads.csv
├── outputs/
└── screenshots/
```

## Design assumptions and limitations
- Roads are undirected and have non-negative distances.
- A parcel is indivisible and can be selected at most once.
- Knapsack optimizes the supplied value score, not deadline feasibility. A production system should reject parcels that cannot be delivered before their deadline and include service time, vehicle limits, traffic, and time windows.
- The nearest-neighbor route is a practical approximation. For larger instances, consider 2-opt improvement, Christofides' algorithm on a metric closure, or a vehicle-routing solver.
- Benchmarking uses repeated runs and averages; very small runtimes are noisy. Use larger inputs and more repetitions for stronger comparisons.
