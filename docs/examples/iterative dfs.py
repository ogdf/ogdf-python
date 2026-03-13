# %%
# This cell generates a random graph for the DFS to run on.

from ogdf_python import ogdf, cppinclude
import cppyy

cppinclude("ogdf/basic/graph_generators/randomized.h")
cppinclude("ogdf/layered/SugiyamaLayout.h")

G = ogdf.Graph()
ogdf.setSeed(1)
ogdf.randomPlanarTriconnectedGraph(G, 10, 20)
G2 = ogdf.Graph()
ogdf.randomPlanarTriconnectedGraph(G2, 5, 10)
G.insert(G2)
GA = ogdf.GraphAttributes(G, ogdf.GraphAttributes.all)
GA.directed = True

SL = ogdf.SugiyamaLayout()
SL.call(GA)
GA.rotateLeft90()
GA

# %%
order = []  # order of visited nodes
index = ogdf.NodeArray[int](G, -1)  # index in order
todo = []  # pending nodes


# %%
def find_next():
    for n in G.nodes:
        if index[n] == -1:
            todo.append((None, n))
            return True
    return False


# %%
def dfs():
    pred, u = todo.pop()

    index[u] = i = len(order)
    order.append(u)

    GA.label[u] = str(i)
    if pred:
        GA.strokeColor[pred] = ogdf.Color("#F00")

    # remove already processed nodes from stack
    while todo and index[todo[-1][1]] >= 0:
        todo.pop()

    # add unprocessed neighbors from stack
    for adj in u.adjEntries:
        v = adj.twinNode()
        if index[v] == -1:
            todo.append((adj.theEdge(), v))


# %%
def dump():
    print("Order", ", ".join(str(n.index()) for n in order))
    print("Todo", ", ".join(str(n.index()) for p, n in todo))
    return GA


# %%
find_next()
dump()

# %%
dfs()
dump()

# %%
dfs()
dump()

# %%
dfs()
dump()

# %%
dfs()
dump()

# %%
# %matplotlib widget
import ipywidgets
from ogdf_python.matplotlib import MatplotlibGraph

w_GA = MatplotlibGraph(GA)
w_todo = ipywidgets.Label()
w_order = ipywidgets.Label()
b_dfs = ipywidgets.Button(description="Step")
b_next = ipywidgets.Button(description="Next Component")
b_reset = ipywidgets.Button(description="Reset")


def update():
    w_GA.update_all()
    w_todo.value = "Todo: " + ", ".join(str(n.index()) for p, n in todo)
    w_order.value = "Order: " + ", ".join(str(n.index()) for n in order)
    b_dfs.disabled = not todo


def b_dfs_click(*args):
    dfs()
    update()


b_dfs.on_click(b_dfs_click)


def b_next_click(*args):
    find_next()
    update()


b_next.on_click(b_next_click)


def b_reset_click(*args):
    order.clear()
    index.fill(-1)
    todo.clear()
    to_reset = ogdf.GraphAttributes.edgeStyle | ogdf.GraphAttributes.nodeLabel
    GA.destroyAttributes(to_reset)
    GA.addAttributes(to_reset)
    update()


b_reset.on_click(b_reset_click)

update()
ipywidgets.VBox(
    [ipywidgets.HBox([b_dfs, b_next, b_reset]), w_todo, w_order, w_GA.ax.figure.canvas]
)
