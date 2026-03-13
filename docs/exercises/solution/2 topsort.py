# %%
# This cell generates a random graph for the topological sort to run on.

%matplotlib widget
from ogdf_python import ogdf, cppinclude
import cppyy

cppinclude("ogdf/basic/graph_generators/randomized.h")
cppinclude("ogdf/layered/SugiyamaLayout.h")
cppinclude("ogdf/basic/simple_graph_alg.h")

G = ogdf.Graph()
GA = ogdf.GraphAttributes(G, ogdf.GraphAttributes.all)
GA.directed = True


def make_graph():
    ogdf.setSeed(1)
    G.clear()
    G2 = ogdf.Graph()
    ogdf.randomPlanarTriconnectedGraph(G2, 10, 20)
    G.insert(G2)
    ogdf.randomPlanarTriconnectedGraph(G2, 5, 10)
    G.insert(G2)
    ogdf.makeAcyclicByReverse(G)

    for e in G.edges:
        GA.label[e] = str(e.index())
    for n in G.nodes:
        GA.label[n] = str(n.index())

    SL = ogdf.SugiyamaLayout()
    SL.call(GA)
    GA.rotateLeft90()

    G.delEdge(G.edges[4])  # add a second source


make_graph()
GA

# %%
good_order = [
    G.nodes[7],
    G.nodes[13],
    G.nodes[12],
    G.nodes[15],
    G.nodes[5],
    G.nodes[11],
    G.nodes[14],
    G.nodes[6],
    G.nodes[10],
    G.nodes[4],
    G.nodes[8],
    G.nodes[3],
    G.nodes[2],
    G.nodes[1],
    G.nodes[9],
    G.nodes[0],
]
bad_order = [
    G.nodes[7],
    G.nodes[13],
    G.nodes[12],
    G.nodes[15],
    G.nodes[5],
    G.nodes[11],
    G.nodes[14],
    G.nodes[6],
    G.nodes[10],
    G.nodes[3],
    G.nodes[8],
    G.nodes[4],
    G.nodes[2],
    G.nodes[1],
    G.nodes[9],
    G.nodes[0],
]


# %%
def validate(order):
    seen = set()
    for n in order:
        for adj in n.adjEntries:
            if not adj.isSource():
                continue
            if not adj.twinNode() in seen:
                print(adj)
                return False
        seen.add(n)
    return True


# %%
validate(good_order)

# %%
validate(bad_order)

# %%
degree = ogdf.NodeArray[int](G, 0)  # degree after node deletion
for n in G.nodes:
    degree[n] = n.outdeg()
    if degree[n] == 0:
        GA.fillColor[n] = ogdf.Color("#FCC")
sinks = [n for n in G.nodes if degree[n] == 0]  # sink nodes

order = []  # order of nodes
index = ogdf.NodeArray[int](G, -1)  # position in order

# %%
import random


def step():
    n = sinks.pop(random.randrange(len(sinks)))
    index[n] = i = len(order)
    order.append(n)

    GA.label[n] = f"{i}"
    GA.strokeColor[n] = ogdf.Color("#666")
    GA.fillColor[n] = ogdf.Color("#CCC")

    # (virtually) remove all edges to n
    for adj in n.adjEntries:
        GA.strokeColor[adj.theEdge()] = ogdf.Color("#CCC")

        if adj.isSource():
            continue
        # else n is the target of the "removed" edge
        # decrement the outdegree of the source of the edge
        degree[adj.twinNode()] -= 1
        if degree[adj.twinNode()] == 0:
            sinks.append(adj.twinNode())
            GA.fillColor[adj.twinNode()] = ogdf.Color("#FCC")


# %%
def dump():
    print("Order:", *order)
    print("Sinks:", *sinks)
    for n in sinks:
        GA.fillColor[n] = ogdf.Color("#FCC")
    return GA


dump()

# %%
step()
dump()

# %%
step()
dump()

# %%
step()
dump()

# %%
import ipywidgets
from ogdf_python.matplotlib import MatplotlibGraph

w = MatplotlibGraph(GA)
w_order = ipywidgets.Label()
w_sinks = ipywidgets.Label()
b_step = ipywidgets.Button(description="Step")
b_reset = ipywidgets.Button(description="Reset")


def update():
    w_order.value = "Order: " + ", ".join(str(n.index()) for n in order)
    w_sinks.value = "Sinks: " + ", ".join(str(n.index()) for n in sinks)
    b_step.disabled = not sinks


def b_step_click(*args):
    step()
    update()
    w.update_node(order[-1])
    for adj in order[-1].adjEntries:
        w.update_edge(adj.theEdge())
    for s in sinks:
        w.update_node(s)


b_step.on_click(b_step_click)


def b_reset_click(*args):
    make_graph()
    order.clear()
    sinks.clear()
    sinks.extend(n for n in G.nodes if n.outdeg() == 0)
    for n in G.nodes:
        degree[n] = n.outdeg()
        if degree[n] == 0:
            GA.fillColor[n] = ogdf.Color("#FCC")
    update()
    w.update_all()


b_reset.on_click(b_reset_click)

update()
ipywidgets.VBox(
    [ipywidgets.HBox([b_step, b_reset]), w_order, w_sinks, w.ax.figure.canvas]
)

# %%
N = list(G.nodes)
print("[", ", ".join(f"G.nodes[{N.index(n)}]" for n in order), "]")

# %%
# allow changing the displayed node label
d_label = ipywidgets.Dropdown(
    options=["Index", "Degree"],
    value="Index",
    description="Node label:",
    disabled=False,
)


def label_changed(change):
    for n in G.nodes:
        if index[n] == -1:
            GA.label[n] = (
                str(n.index()) if change["new"] == "Index" else f"d{degree[n]}"
            )
    w.update_all()


d_label.observe(label_changed, names="value")
d_label
