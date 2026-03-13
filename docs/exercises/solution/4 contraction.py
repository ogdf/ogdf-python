# %%
%matplotlib widget
from ogdf_python import ogdf, cppinclude
from itertools import combinations

cppinclude("ogdf/basic/simple_graph_alg.h")

G = ogdf.Graph()
GA = ogdf.GraphAttributes(G, ogdf.GraphAttributes.all)
N = []
E = []

name = ogdf.NodeArray[str](G, "")


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
            GA.label[n] = name[n] = f"{g}-{i}"
    for e in G.edges:
        GA.label[e] = str(e.index())
    draw(N[0], 0, 500)
    draw(N[1], 500, 500, True)
    draw(N[2], 500, 500)
    draw(N[3], 0, 500, True)


#     G.delEdge(G.searchEdge(N[0][3], N[1][0]))
#     G.delEdge(G.searchEdge(N[0][2], N[2][1]))
#     G.delEdge(G.searchEdge(N[0][1], N[3][1]))
#     G.delEdge(G.searchEdge(N[3][2], N[1][0]))
#     G.delEdge(G.searchEdge(N[3][1], N[1][1]))
#     G.delEdge(G.searchEdge(N[3][0], N[2][0]))
#     G.delEdge(G.searchEdge(N[3][0], N[2][2]))


# %%
mark = ogdf.NodeArray["ogdf::List<ogdf::adjEntry>"](G)
red = ogdf.EdgeArray[bool](G, False)
deg = ogdf.NodeArray[int](G, 0)
maxdeg = 0


def make_red(e):
    global maxdeg
    if not red[e]:
        # print(f"Making edge {e!r} red, counters:", deg[e.source()], deg[e.target()], maxdeg)
        GA.strokeColor[e] = ogdf.Color("#F00")
        red[e] = True
        deg[e.source()] += 1
        deg[e.target()] += 1
        maxdeg = max(deg[e.source()], deg[e.target()], maxdeg)


def contract_id(g1, n1, g2, n2):
    a = N[g1][n1]
    b = N[g2][n2]
    contract(a, b)
    N[g2][n2] = a


def contract(a, b):
    for adj in list(a.adjEntries):
        if adj.twinNode() == b:
            if red[adj.theEdge()]:
                deg[a] -= 1
            G.delEdge(adj.theEdge())
        else:
            mark[adj.twinNode()].pushBack(adj)
    for adj in b.adjEntries:
        mark[adj.twinNode()].pushBack(adj)

    for adj in a.adjEntries:
        if len(mark[adj.twinNode()]) == 1:
            make_red(adj.theEdge())
            mark[adj.twinNode()].clear()

    for adj in list(b.adjEntries):
        e = adj.theEdge()

        if len(mark[adj.twinNode()]) == 1:
            mark[adj.twinNode()].clear()
            # print(f"Move {e!r} {red[e]}")
            if adj.isSource():
                G.moveSource(e, a)  # breaks adj
            else:
                G.moveTarget(e, a)
            if red[e]:
                deg[a] += 1
            else:
                make_red(e)

        else:
            e0 = mark[adj.twinNode()].front().theEdge()
            assert e != e0
            # print(f"Delete {e!r} {red[e]}")
            if red[e]:
                deg[adj.twinNode()] -= 1
                make_red(e0)
            mark[adj.twinNode()].clear()
            G.delEdge(e)  # breaks adj

    #     GA.x[b] = GA.x[a]
    #     GA.y[b] = GA.y[a]
    G.delNode(b)

    # print(maxdeg, ogdf.isSimpleUndirected(G))


# %%
def check_deg(n):
    count = sum(1 for adj in n.adjEntries if red[adj])
    if count != deg[n]:
        print(f"Node {n} has {count} red edges, but counter said {deg[n]}!")
    if not mark[n].empty():
        print(f"Node {n} has {mark[n].size()} marks left over!")
    return count, n.index(), n


def check_degs():
    maxcnt, _, n = max(check_deg(n) for n in G.nodes)
    assert maxcnt <= maxdeg


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
        for n in G.nodes:
            GA.label[n] = name[n] + "\n" + str(deg[n])
        w_GA.update_all()
        selected = None
        check_degs()
    else:
        selected = n
        GA.fillColor[selected] = ogdf.Color("#CCF")
        w_GA.update_node(n)


w_GA.on_node_click = on_node_click


def reset():
    global maxdeg
    maxdeg = 0
    GA.init(GA.all)
    make_graph()
    mark.fill(ogdf.List["ogdf::adjEntry"]())
    red.fill(False)
    deg.fill(0)


b_reset = ipywidgets.Button(description="Reset")


def b_reset_click(*args):
    reset()
    w_GA.update_all()


b_reset.on_click(b_reset_click)

make_graph()
ipywidgets.VBox([b_reset, w_GA.ax.figure.canvas])


# %%
import cppyy.ll


def random_seq():
    a = G.chooseNode()
    b = G.chooseNode(lambda n: n != a)
    if cppyy.ll.addressof(b) == 0:  # no second node found
        return False
    print(f"contract({GA.label[a]}, {GA.label[b]})")
    contract(a, b)
    check_degs()
    print(maxdeg, {str(GA.label[n]): deg[n] for n in G.nodes})
    print()
    return True


# %%
reset()
while random_seq():
    pass
assert G.numberOfNodes() == 1
