# %%
# This cell generates a random graph for the DFS to run on.

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
    ogdf.randomPlanarTriconnectedGraph(G, 10, 20)
    G2 = ogdf.Graph()
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


make_graph()
GA

# %%
G.delEdge(G.edges[4])
GA

# %%
sinks = [n for n in G.nodes if n.outdeg() == 0]  # sink nodes
order = []


# %%
def step():
    n = sinks.pop()
    # n and its adjEntries will be gone after deletion, store its index and neighbor nodes:
    order.append(n.index())
    neighs = [adj.twinNode() for adj in n.adjEntries]
    G.delNode(n)
    # add all neighbors that now have out degree 0 as sinks
    sinks.extend(n for n in neighs if n.outdeg() == 0)
    return neighs


# %%
def dump():
    print("Order:", order)
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
step()
dump()

# %%
# %matplotlib widget
import ipywidgets
from ogdf_python.matplotlib import MatplotlibGraph

w_GA = MatplotlibGraph(GA)
w_order = ipywidgets.Label()
w_sinks = ipywidgets.Label()
b_step = ipywidgets.Button(description="Step")
b_reset = ipywidgets.Button(description="Reset")


def update():
    for n in sinks:
        GA.fillColor[n] = ogdf.Color("#FCC")
        w_GA.update_node(n)
    w_order.value = "Order: " + ", ".join(str(n) for n in order)
    w_sinks.value = "Sinks: " + ", ".join(str(n.index()) for n in sinks)
    b_step.disabled = not sinks


def b_step_click(*args):
    step()
    update()


b_step.on_click(b_step_click)


def b_reset_click(*args):
    make_graph()
    order.clear()
    sinks.clear()
    sinks.extend(n for n in G.nodes if n.outdeg() == 0)
    update()
    w_GA.update_all()


b_reset.on_click(b_reset_click)

update()
ipywidgets.VBox(
    [ipywidgets.HBox([b_step, b_reset]), w_order, w_sinks, w_GA.ax.figure.canvas]
)
