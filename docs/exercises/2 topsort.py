# %%
# This cell generates a random graph for the topological sort to run on.

# %matplotlib widget
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

# %% [markdown]
# The structure of the following cells may provide some guidelines, but feel free to make changes as you see fit. The dots are only a hint at where additions are probably neccesary.

# %%
# TODO define which data you want to store
order = []  # order of nodes
outdeg = ogdf.NodeArray[int](G, 0)  # outdegree after node deletion
...


# %%
# TODO implement the algorithm in this reusable function
# this should work similar to the DFS example
def topo_step(): ...


# %%
# TODO this method should print information about the current state and return GA for display
def dump():
    print("Order:", ...)
    ...
    return GA


dump()

# %%
topo_step()
dump()

# %%
# when using "Run All Cells" these repeated cells show multiple consecutive steps
topo_step()
dump()

# %%
topo_step()
dump()

# %%
# Bonus: use the following scaffolding for an interactive UI for your implementation
import ipywidgets
from ogdf_python.matplotlib import MatplotlibGraph

reset()
w = MatplotlibGraph(GA)
w_order = ipywidgets.Label()
b_step = ipywidgets.Button(description="Step")
b_reset = ipywidgets.Button(description="Reset")


def update():
    w_order.value = "Order: " + ...
    ...
    w.update_all()


def b_step_click(*args):
    topo_step()
    update()


b_step.on_click(b_step_click)


def b_reset_click(*args):
    make_graph()
    ...
    update()


b_reset.on_click(b_reset_click)

update()
ipywidgets.VBox(
    [ipywidgets.HBox([b_step, b_reset]), w_order, w_sources, w.ax.figure.canvas]
)

# %%
# use this if you want to allow changing the displayed node label

d_label = ipywidgets.Dropdown(
    options=["Index", "Degree"],
    value="Index",
    description="Node label:",
    disabled=False,
)


def label_changed(change):
    for n in G.nodes:
        GA.label[n] = str(n.index()) if change["new"] == "Index" else f"d{outdeg[n]}"
    w.update_all()


d_label.observe(label_changed, names="value")
d_label
