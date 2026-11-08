"""Generate small/large synthetic data and compare algorithm runtimes."""
import csv, random, time
from pathlib import Path
import matplotlib.pyplot as plt
from main import load_parcels, load_graph, prioritize, knapsack, dijkstra, nearest_neighbor_tsp

ROOT = Path(__file__).resolve().parent
OUT = ROOT/"outputs"; OUT.mkdir(exist_ok=True)

def make_case(folder, n, nodes):
    folder.mkdir(exist_ok=True)
    rng = random.Random(100+n)
    names = ["DEPOT"] + [f"N{i}" for i in range(1,nodes)]
    with (folder/"parcels.csv").open("w", newline="") as f:
        w=csv.writer(f); w.writerow(["id","weight","value","deadline","priority","destination"])
        for i in range(n):
            w.writerow([f"X{i:04d}",rng.randint(1,10),rng.randint(5,60),rng.randint(1,30),rng.randint(1,5),rng.choice(names[1:])])
    edges=set()
    # Connected ring plus random extra edges.
    for i in range(len(names)): edges.add(tuple(sorted((names[i],names[(i+1)%len(names)]))))
    while len(edges) < min(nodes*(nodes-1)//2, nodes*3):
        a,b=rng.sample(names,2); edges.add(tuple(sorted((a,b))))
    with (folder/"roads.csv").open("w",newline="") as f:
        w=csv.writer(f); w.writerow(["from","to","distance"])
        for a,b in sorted(edges): w.writerow([a,b,rng.randint(1,20)])

def avg(fn, repeats=5):
    vals=[]
    for _ in range(repeats):
        t=time.perf_counter(); fn(); vals.append(time.perf_counter()-t)
    return sum(vals)/len(vals)

cases=[("Small",60,12,20),("Large",450,45,60)]
rows=[]
for label,n,nodes,cap in cases:
    folder=ROOT/"data"/("bench_"+label.lower()); make_case(folder,n,nodes)
    ps=load_parcels(folder/"parcels.csv"); g=load_graph(folder/"roads.csv")
    ordered=prioritize(ps); selected,_,_=knapsack(ordered,cap)
    targets=list(dict.fromkeys(p["destination"] for p in selected))[:min(12,nodes-1)]
    rows.append({"dataset":label,"parcels":n,"nodes":nodes,
      "merge_sort_ms":avg(lambda:prioritize(ps))*1000,
      "knapsack_ms":avg(lambda:knapsack(ordered,cap))*1000,
      "dijkstra_ms":avg(lambda:dijkstra(g,"DEPOT"))*1000,
      "nearest_neighbor_tsp_ms":avg(lambda:nearest_neighbor_tsp(g,"DEPOT",targets))*1000})
with (OUT/"benchmark.csv").open("w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
labels=["Merge sort","Knapsack DP","Dijkstra","Nearest-neighbor TSP"]
keys=["merge_sort_ms","knapsack_ms","dijkstra_ms","nearest_neighbor_tsp_ms"]
x=range(len(labels)); width=.35
fig,ax=plt.subplots(figsize=(10,5))
for idx,row in enumerate(rows):
    ax.bar([v+(idx-.5)*width for v in x],[row[k] for k in keys],width,label=f'{row["dataset"]} ({row["parcels"]} parcels)')
ax.set_xticks(list(x),labels); ax.set_ylabel("Average runtime (ms)"); ax.set_title("Courier algorithm runtime comparison")
ax.legend(); ax.grid(axis="y",alpha=.25); fig.tight_layout()
fig.savefig(OUT/"runtime_comparison.png",dpi=160)
print("Benchmark written to outputs/benchmark.csv")
print("Chart written to outputs/runtime_comparison.png")
for row in rows: print(row)
