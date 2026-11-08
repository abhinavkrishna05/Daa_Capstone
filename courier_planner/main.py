"""Integrated courier planning application: sorting, knapsack, shortest paths and TSP."""
from __future__ import annotations
import argparse, csv, heapq, json, random, time
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path(__file__).resolve().parent

def load_parcels(path: Path) -> List[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for p in rows:
        for k in ("weight", "value", "deadline", "priority"):
            p[k] = int(p[k])
    return rows

def merge_sort(items: List[dict], key=lambda x: x["deadline"]) -> List[dict]:
    """Stable O(n log n) merge sort."""
    if len(items) <= 1:
        return items[:]
    mid = len(items)//2
    left, right = merge_sort(items[:mid], key), merge_sort(items[mid:], key)
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    return out + left[i:] + right[j:]

def prioritize(parcels: List[dict]) -> List[dict]:
    # Earliest deadline first; higher priority breaks ties.
    return merge_sort(parcels, key=lambda p: (p["deadline"], -p["priority"]))

def knapsack(parcels: List[dict], capacity: int) -> Tuple[List[dict], int, list]:
    """0/1 knapsack DP. Returns selected parcels, max value and DP table."""
    n = len(parcels)
    dp = [[0]*(capacity+1) for _ in range(n+1)]
    for i, p in enumerate(parcels, 1):
        for cap in range(capacity+1):
            dp[i][cap] = dp[i-1][cap]
            if p["weight"] <= cap:
                dp[i][cap] = max(dp[i][cap], p["value"] + dp[i-1][cap-p["weight"]])
    chosen, cap = [], capacity
    for i in range(n, 0, -1):
        if dp[i][cap] != dp[i-1][cap]:
            chosen.append(parcels[i-1])
            cap -= parcels[i-1]["weight"]
    chosen.reverse()
    return chosen, dp[n][capacity], dp

def load_graph(path: Path) -> Dict[str, Dict[str, int]]:
    graph: Dict[str, Dict[str, int]] = {}
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            a, b, w = row["from"], row["to"], int(row["distance"])
            graph.setdefault(a, {})[b] = w
            graph.setdefault(b, {})[a] = w
    return graph

def dijkstra(graph: Dict[str, Dict[str, int]], start: str):
    dist = {v: float("inf") for v in graph}
    prev = {v: None for v in graph}
    if start not in graph:
        raise ValueError(f"Unknown start node: {start}")
    dist[start] = 0
    pq = [(0, start)]
    while pq:
        d, u = heapq.heappop(pq)
        if d != dist[u]: continue
        for v, w in graph[u].items():
            nd = d + w
            if nd < dist[v]:
                dist[v], prev[v] = nd, u
                heapq.heappush(pq, (nd, v))
    return dist, prev

def reconstruct(prev, target):
    path, cur = [], target
    while cur is not None:
        path.append(cur); cur = prev[cur]
    return list(reversed(path))

def nearest_neighbor_tsp(graph, start, targets):
    """Approximate a tour; each leg uses Dijkstra shortest-path distance."""
    remaining = set(targets) - {start}
    route, total, legs = [start], 0, []
    current = start
    while remaining:
        dist, prev = dijkstra(graph, current)
        reachable = [(dist[v], v) for v in remaining if dist.get(v, float("inf")) < float("inf")]
        if not reachable:
            raise ValueError(f"Unreachable delivery points: {sorted(remaining)}")
        leg_distance, nxt = min(reachable)
        leg_path = reconstruct(prev, nxt)
        legs.append({"from": current, "to": nxt, "path": leg_path, "distance": int(leg_distance)})
        total += leg_distance
        route.append(nxt); remaining.remove(nxt); current = nxt
    dist, prev = dijkstra(graph, current)
    if start in dist and dist[start] < float("inf") and current != start:
        back = dist[start]
        legs.append({"from": current, "to": start, "path": reconstruct(prev, start), "distance": int(back)})
        total += back; route.append(start)
    return route, int(total), legs

def benchmark(parcels, graph, capacity, start, targets, repeats=3):
    timings = {}
    funcs = {
        "Merge sort": lambda: prioritize(parcels),
        "Knapsack DP": lambda: knapsack(parcels, capacity),
        "Dijkstra": lambda: dijkstra(graph, start),
        "Nearest-neighbor TSP": lambda: nearest_neighbor_tsp(graph, start, targets),
    }
    for name, fn in funcs.items():
        samples = []
        for _ in range(repeats):
            t0 = time.perf_counter(); fn(); samples.append(time.perf_counter()-t0)
        timings[name] = sum(samples)/len(samples)
    return timings

def run(data_dir: Path, capacity: int, start: str, output_dir: Path):
    parcels = load_parcels(data_dir/"parcels.csv")
    graph = load_graph(data_dir/"roads.csv")
    ordered = prioritize(parcels)
    selected, value, dp = knapsack(ordered, capacity)
    targets = sorted({p["destination"] for p in selected})
    if not targets: targets = [start]
    route, distance, legs = nearest_neighbor_tsp(graph, start, targets)
    timings = benchmark(parcels, graph, capacity, start, targets)
    output_dir.mkdir(parents=True, exist_ok=True)
    result = {
        "sorted_parcels": [p["id"] for p in ordered],
        "selected_parcels": [p["id"] for p in selected],
        "selected_weight": sum(p["weight"] for p in selected),
        "capacity": capacity, "total_value": value,
        "delivery_points": targets, "route": route,
        "route_distance_km": distance, "route_legs": legs,
        "runtime_seconds": timings,
    }
    (output_dir/"result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    (output_dir/"dp_table.json").write_text(json.dumps(dp), encoding="utf-8")
    return result, ordered, selected, timings

def main():
    ap = argparse.ArgumentParser(description="Integrated Courier Planning System")
    ap.add_argument("--data", type=Path, default=ROOT/"data")
    ap.add_argument("--capacity", type=int, default=20)
    ap.add_argument("--start", default="DEPOT")
    ap.add_argument("--output", type=Path, default=ROOT/"outputs")
    args = ap.parse_args()
    result, ordered, selected, timings = run(args.data, args.capacity, args.start, args.output)
    print("\\n=== COURIER PLANNING SYSTEM ===")
    print("Prioritized parcels:", " -> ".join(p["id"] for p in ordered))
    print("Selected parcels:", ", ".join(p["id"] for p in selected) or "None")
    print(f"Packed weight: {result['selected_weight']}/{args.capacity} kg | Value: {result['total_value']}")
    print("Delivery route:", " -> ".join(result["route"]))
    print(f"Total route distance: {result['route_distance_km']} km")
    print("\\nRuntime (mean of 3 runs):")
    for name, seconds in timings.items(): print(f"  {name:24s} {seconds*1000:.4f} ms")
    print(f"\\nDetailed results saved to: {args.output}")

if __name__ == "__main__": main()
