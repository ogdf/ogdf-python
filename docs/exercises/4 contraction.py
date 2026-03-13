# %%
%matplotlib widget
from ogdf_python import ogdf, cppinclude
from itertools import combinations

cppinclude("ogdf/basic/simple_graph_alg.h")

G = ogdf.Graph()
GA = ogdf.GraphAttributes(G, ogdf.GraphAttributes.all)
N = []
E = []


def mknodes(x):
    return [G.newNode() for _ in range(x)]


def connect(A, B):
    return [G.newEdge(a, b) for a in A for b in B]


def draw(ns, height=0, width=500, flip=False):
    for i, n in enumerate(ns):
        GA.y[n] = height
        GA.x[n] = ((i + 1) / (len(ns) + 1)) * width
        if flip:
            GA.y[n], GA.x[n] = GA.x[n], GA.y[n]


def make_graph():
    G.clear()
    N.clear()
    N.extend([mknodes(4), mknodes(2), mknodes(3), mknodes(3)])
    E.clear()
    E.extend([connect(N[A], N[B]) for A, B in combinations(range(len(N)), 2)])

    for g, ns in enumerate(N):
        for i, n in enumerate(ns):
            GA.label[n] = f"{g}-{i}"
    for e in G.edges:
        GA.label[e] = str(e)
    draw(N[0], 0, 500)
    draw(N[1], 500, 500, True)
    draw(N[2], 500, 500)
    draw(N[3], 0, 500, True)


# %%
def contract(a, b): ...


# %%
def check_degs(): ...


# %%
def reset():
    make_graph()


# %%
import ipywidgets
from ogdf_python.matplotlib import MatplotlibGraph

w_GA = MatplotlibGraph(GA)
selected = None


def on_node_click(n, event):
    global selected
    if selected:
        GA.fillColor[selected] = ogdf.Color("#FFF")
        contract(selected, n)
        w_GA.update_all()
        selected = None
        check_degs()
    else:
        selected = n
        GA.fillColor[selected] = ogdf.Color("#CCF")
        w_GA.update_node(n)


w_GA.on_node_click = on_node_click

b_reset = ipywidgets.Button(description="Reset")


def b_reset_click(*args):
    reset()
    w_GA.update_all()


b_reset.on_click(b_reset_click)

make_graph()
ipywidgets.VBox([b_reset, w_GA.ax.figure.canvas])

# %% [markdown]
# Example sequence for debugging:
# ```
# contract(2-0, 2-2)
# 0 {'0-0': 0, '0-1': 0, '0-2': 0, '0-3': 0, '1-0': 0, '1-1': 0, '2-0': 0, '2-1': 0, '3-0': 0, '3-1': 0, '3-2': 0}
#
# contract(0-1, 0-3)
# 0 {'0-0': 0, '0-1': 0, '0-2': 0, '1-0': 0, '1-1': 0, '2-0': 0, '2-1': 0, '3-0': 0, '3-1': 0, '3-2': 0}
#
# contract(3-1, 0-0)
# 4 {'0-1': 1, '0-2': 1, '1-0': 0, '1-1': 0, '2-0': 0, '2-1': 0, '3-0': 1, '3-1': 4, '3-2': 1}
#
# contract(3-1, 1-0)
# 5 {'0-1': 1, '0-2': 1, '1-1': 1, '2-0': 0, '2-1': 0, '3-0': 1, '3-1': 5, '3-2': 1}
#
# contract(3-0, 0-2)
# 5 {'0-1': 2, '1-1': 1, '2-0': 0, '2-1': 0, '3-0': 3, '3-1': 4, '3-2': 2}
#
# contract(1-1, 3-0)
# 5 {'0-1': 2, '1-1': 3, '2-0': 0, '2-1': 0, '3-1': 3, '3-2': 2}
#
# contract(2-0, 2-1)
# 5 {'0-1': 2, '1-1': 3, '2-0': 0, '3-1': 3, '3-2': 2}
#
# contract(3-2, 0-1)
# 5 {'1-1': 2, '2-0': 0, '3-1': 2, '3-2': 2}
#
# contract(3-1, 3-2)
# 5 {'1-1': 1, '2-0': 0, '3-1': 1}
#
# contract(2-0, 1-1)
# 5 {'2-0': 1, '3-1': 1}
#
# contract(2-0, 3-1)
# 5 {'2-0': 0}
# ```
