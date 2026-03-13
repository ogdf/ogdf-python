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
def cmp(a, b):  # comparator function for two nodes a, b
    return ...


# create PriorityQueue of nodes with the given comparator function
cppinclude("ogdf/basic/PriorityQueue.h")
todo = ogdf.PriorityQueue[
    "ogdf::node", "std::function<bool(ogdf::node, ogdf::node)>", "ogdf::PairingHeap"
](cmp)

# this node array can be used to store the position of nodes in the priority queue for decreasing their key
null_pqnode = cppyy.bind_object(cppyy.nullptr, "ogdf::PairingHeapNode<ogdf::node>")
handles = ogdf.NodeArray["ogdf::PairingHeapNode<ogdf::node>*"](G, null_pqnode)

# see help(todo) and the C++ Docs for more information


# %%
def step(): ...


# %%
import ipywidgets
from ogdf_python.matplotlib import MatplotlibGraph

w = MatplotlibGraph(GA)
w_todo = ipywidgets.Label()
b_step = ipywidgets.Button(description="Step")


def b_step_click(*args): ...


b_step.on_click(b_step_click)

ipywidgets.VBox([b_step, w_todo, w.ax.figure.canvas])
