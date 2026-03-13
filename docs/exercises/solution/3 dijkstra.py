# %%
%matplotlib widget
from ogdf_python import ogdf, cppinclude, cppdef
import cppyy

cppinclude("ogdf/basic/graph_generators/randomized.h")
cppinclude("ogdf/layered/SugiyamaLayout.h")
null_edge = cppyy.bind_object(cppyy.nullptr, "ogdf::EdgeElement")

G = ogdf.Graph()
ogdf.setSeed(1)
ogdf.randomPlanarCNBGraph(G, 10, 20, 3)
# G2 = ogdf.Graph()
# ogdf.randomPlanarTriconnectedGraph(G2, 5, 10)
# G.insert(G2)
GA = ogdf.GraphAttributes(G, ogdf.GraphAttributes.all)
GA.directed = True

for n in G.nodes:
    GA.label[n] = str(n.index())
s = G.nodes[0]
GA.strokeColor[s] = ogdf.Color("#0C0")

SL = ogdf.SugiyamaLayout()
SL.call(GA)
GA.rotateLeft90()
GA

# %%
done = ogdf.NodeArray[bool](G, False)
dist = ogdf.NodeArray[int](G, -1)
pred = ogdf.NodeArray["ogdf::edge"](G, null_edge)
dist[s] = 0

# %%
import heapq

todo = [(0, 0, s)]


def peek():
    return todo[0][2]


def pop():
    _, _, u = heapq.heappop(todo)
    assert not done[u]
    while todo and done[peek()]:  # ensure topmost node is never done
        heapq.heappop(todo)
    return u


def push(v):
    heapq.heappush(todo, (dist[v], v.index(), v))


def empty():
    return len(todo) == 0


# %%
def step():
    assert not empty()
    u = pop()

    for adj in u.adjEntries:
        v = adj.twinNode()
        if dist[v] < 0 or dist[v] > dist[u] + 1:
            assert not done[v]
            dist[v] = dist[u] + 1
            pred[v] = adj.theEdge()
            push(v)
            GA.fillColor[v] = ogdf.Color("#CCC")

    done[u] = True
    GA.fillColor[u] = ogdf.Color("#666")
    if pred[u] != null_edge:
        GA.strokeColor[pred[u]] = ogdf.Color("#F00")


# %%
import ipywidgets
from ogdf_python.matplotlib import MatplotlibGraph

w_GA = MatplotlibGraph(GA)
w_todo = ipywidgets.Label()
b_step = ipywidgets.Button(description="Step")


def b_step_click(*args):
    step()
    if not empty():
        GA.strokeColor[peek()] = ogdf.Color("#F00")
    w_GA.update_all()
    w_todo.value = "Todo: " + ", ".join(f"{n.index()}@{d}" for d, i, n in todo)
    b_step.disabled = empty()


b_step.on_click(b_step_click)

ipywidgets.VBox([b_step, w_todo, w_GA.ax.figure.canvas])

# %%
cppinclude("ogdf/graphalg/ShortestPathAlgorithms.h")
sourceNode = G.nodes[0]
distances = ogdf.NodeArray[int](G)
edgeCost = 1
ogdf.bfs_SPSS[int](sourceNode, G, distances, edgeCost)

print(dist)
print(distances)

# %%
weights = ogdf.EdgeArray["double"](G, 1.0)
# for e in G.edges:
#    weights[e] = GA.doubleWeight[e]

distances = ogdf.NodeArray["double"](G)
predecessors = ogdf.NodeArray[ogdf.edge](G)

cppinclude("ogdf/graphalg/Dijkstra.h")
sssp = ogdf.Dijkstra["double", "ogdf::PairingHeap"]()
sssp.call(G, weights, G.nodes[0], predecessors, distances, directed=True)

distances
