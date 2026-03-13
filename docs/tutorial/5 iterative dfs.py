# %%
# In this notebook, we are going to implement an undirected depth-first search.
# This first cell generates a sufficiently big graph for the DFS to run on.

from ogdf_python import ogdf, cppinclude

cppinclude("ogdf/basic/graph_generators/randomized.h")
cppinclude("ogdf/layered/SugiyamaLayout.h")

G = ogdf.Graph()
ogdf.setSeed(1)
ogdf.randomPlanarTriconnectedGraph(G, 10, 20)
G2 = ogdf.Graph()
ogdf.randomPlanarTriconnectedGraph(G2, 5, 10)
G.insert(G2)

GA = ogdf.GraphAttributes(G, ogdf.GraphAttributes.all)
SL = ogdf.SugiyamaLayout()
SL.call(GA)
GA.rotateLeft90()
for n in G.nodes:
    GA.label[n] = str(n.index())
GA

# %% [markdown]
# For the DFS we are going to store the output order of nodes in a list, a mapping telling us for every node at which index in the order it was inserted, and a list/queue of tuples consisting of pending nodes, preceded by the edge via which they were encountered.
#
# `NodeArray`s (and similarly `Edge`- and `AdjEntryArrays`) label the nodes of the graph that is passed as first constructor argument.
# `GraphAttributes` uses `Node-` and `EdgeArrays` to store all attributes, but custom `NodeArray` instances allow storing data that `GraphAttributes` can't accomodate.
# The type of the contained values needs to be passed in square brackets (i.e. as C++ template parameter for the underlying `ogdf::NodeArray<T>`).
# The second constructor argument is the optional default value for nodes that have no value assigned yet (or have been inserted after creation of the NodeArray).
# Values can be accessed similarly to python dicts via `index[x]`, but are always present (i.e. no `val in dict` checking, so NodeArrays are more like `defaultdict`s).
# The main point about `NodeArray`s is that the implementation is much more efficient than python `dict`s!

# %%
order = []  # order of visited nodes
index = ogdf.NodeArray[int](G, -1)  # index in order
todo = []  # pending nodes

# %%
help(ogdf.NodeArray)


# %%
def find_next():
    # This method searches for the next unprocessed nodes and queues it.
    # We set the source edge to None in the tuple `(None, n)` because
    # the root of the DFS tree has no incoming edge.
    for n in G.nodes:
        if index[n] == -1:
            todo.append((None, n))
            return True

    return False


# %%
def dfs_step():
    pred, u = todo.pop()  # retrieve next tuple and unpack it
    # `pred` is the edge via which we found `u`, or None if `u` is a root

    # insert u into order and set its index
    index[u] = i = len(order)
    order.append(u)

    # update the drawing
    GA.fillColor[u] = ogdf.Color("#FC0")
    if pred:
        GA.strokeColor[pred] = ogdf.Color("#F00")

    # remove already processed nodes from stack
    while todo and index[todo[-1][1]] >= 0:
        todo.pop()

    # add unprocessed neighbors to stack
    for adj in u.adjEntries:
        v = adj.twinNode()
        if adj.isSource() and index[v] == -1:
            todo.append((adj.theEdge(), v))


# %%
def dump():  # utility function for easily displaying the current state
    print("Order", ", ".join(str(n.index()) for n in order))
    print("Todo", ", ".join(str(n.index()) for p, n in todo))
    return GA


# %%
# Run this and the following cells one after another to see the DFS progress...
find_next()
dump()

# %%
dfs_step()
dump()

# %%
dfs_step()
dump()

# %%
dfs_step()
dump()

# %%
dfs_step()
dump()

# %%
# More comfortable than multiple consecutive cells with the same contents is
# a UI for executing the algorithm step-by-step. That's what we'll build here.

# enable the interactive widget
# %matplotlib widget
# try having G or GA as last statement in a cell after running the above line!

import ipywidgets
from ogdf_python.matplotlib import MatplotlibGraph

w = MatplotlibGraph(GA)  # widget for displaying a drawing
w_todo = ipywidgets.Label()  # text labels
w_order = ipywidgets.Label()
b_dfs = ipywidgets.Button(description="Step")  # interactive buttons
b_next = ipywidgets.Button(description="Next Component")
b_reset = ipywidgets.Button(description="Reset")


def update():
    # update all UI elements
    w.update_all()
    w_todo.value = "Todo: " + ", ".join(str(n.index()) for p, n in todo)
    w_order.value = "Order: " + ", ".join(str(n.index()) for n in order)
    b_dfs.disabled = not todo


def b_dfs_click(b):
    # when clicking the "Step" button, execute one DFS step and update the UI
    dfs_step()
    update()


b_dfs.on_click(b_dfs_click)  # functions are objects, too!


def b_next_click(b):
    # continue to the next (or first) connected component
    find_next()
    update()


b_next.on_click(b_next_click)


def b_reset_click(b):
    # reset the DFS to the initial empty state
    order.clear()
    index.fill(-1)
    todo.clear()
    to_reset = ogdf.GraphAttributes.edgeStyle | ogdf.GraphAttributes.nodeStyle
    GA.destroyAttributes(to_reset)
    GA.addAttributes(to_reset)
    update()


b_reset.on_click(b_reset_click)


update()
# V- and HBoxes arrange multiple UI widgets next to each other
# as for G and GA, the UI element on the last line of a cell will be rendered below it
ipywidgets.VBox(
    [ipywidgets.HBox([b_dfs, b_next, b_reset]), w_todo, w_order, w.ax.figure.canvas]
)
