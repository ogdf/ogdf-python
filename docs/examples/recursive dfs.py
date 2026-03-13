# %%
# This cell generates a random graph for the DFS to run on.

import cppyy

# # %env OGDF_BUILD_DIR=~/ogdf/build-debug
# uncomment if you didn't set this globally
from ogdf_python import ogdf, cppinclude

cppinclude("ogdf/basic/graph_generators/randomized.h")
cppinclude("ogdf/layered/SugiyamaLayout.h")
null_node = cppyy.bind_object(cppyy.nullptr, "ogdf::NodeElement")

G = ogdf.Graph()
ogdf.setSeed(1)
ogdf.randomPlanarTriconnectedGraph(G, 10, 20)
GA = ogdf.GraphAttributes(G, ogdf.GraphAttributes.all)
GA.directed = True

SL = ogdf.SugiyamaLayout()
SL.call(GA)
GA.rotateRight90()


# %%
# This is the main DFS code. Compare it with the slides from the lecture!


def dfs(G):
    # NodeArrays are used to store information "labelling" individual nodes
    discovery = ogdf.NodeArray[int](G, -1)
    finish = ogdf.NodeArray[int](G, -1)
    predecessor = ogdf.NodeArray["ogdf::node"](G, null_node)

    time = 0

    def dfs_visit(u):
        nonlocal time  # (we need to overwrite this variable from the parent function)

        time += 1
        discovery[u] = time
        # yield stops the execution of our method and passes the variables to our caller
        yield u, discovery, finish, predecessor
        # the code will continue here the next time `next(it)` is called

        for adj in u.adjEntries:
            v = adj.twinNode()
            if adj.isSource() and discovery[v] < 0:
                predecessor[v] = u
                # yield from simply "copies over" all yield statements from the called method
                yield from dfs_visit(v)

        time += 1
        finish[u] = time
        # yield again to report the state after
        yield u, discovery, finish, predecessor

    for node in G.nodes:
        if discovery[node] < 0:
            yield from dfs_visit(node)


# %%
# This cell (re-)starts the DFS and (re-)initializes the drawing of the graph

last = None
for u in G.nodes:
    GA.label[u] = ""
    GA.strokeColor[u] = ogdf.Color(230, 230, 230)
    GA.width[u] = 40
    GA.fillColor[u] = ogdf.Color(ogdf.Color.Name.White)
for e in G.edges:
    GA.strokeColor[e] = ogdf.Color(150, 150, 150)
it = dfs(G)
GA


# %% pycharm={"name": "#%%\n"}
# This method executes one DFS step and then visualizes the current state


def make_step():
    global it, last
    try:
        # !!! This is the important line:
        u, discovery, finish, predecessor = next(it)
        # All the following code is just for updating the visualisation
        d = discovery[u]
        f = finish[u]
        GA.label[u] = "(%s, %s)" % (d, f)
        print(GA.label[u])

        if f < 0:
            GA.strokeColor[u] = ogdf.Color(150, 150, 150)
        else:
            GA.strokeColor[u] = ogdf.Color(0, 0, 0)

        for adj in u.adjEntries:
            e = adj.theEdge()
            ds = discovery[e.source()]
            fs = finish[e.source()]
            dt = discovery[e.target()]
            ft = finish[e.target()]

            if ds < 0:
                continue
            elif predecessor[e.target()] == e.source():
                GA.strokeColor[e] = ogdf.Color(ogdf.Color.Name.Darkblue)
            elif dt >= 0 and dt < ds:
                if ft >= 0 and fs > ft:
                    GA.strokeColor[e] = ogdf.Color(ogdf.Color.Name.Pink)  # FIXME
                else:
                    GA.strokeColor[e] = ogdf.Color(ogdf.Color.Name.Lightgreen)
            elif ds < dt:
                GA.strokeColor[e] = ogdf.Color(ogdf.Color.Name.Lightblue)

        if last is not None:
            GA.fillColor[last] = ogdf.Color(255, 255, 255)
        GA.fillColor[u] = ogdf.Color(ogdf.Color.Name.Lightpink)
        last = u

    except StopIteration as e:
        print("done", e.args)
    return GA


# %% pycharm={"name": "#%%\n"}
make_step()

# You can also run this cell multiple times to see the graph being updated
# For the static version of this notebook I included the next steps separately

# %% pycharm={"name": "#%%\n"}
make_step()

# %% pycharm={"name": "#%%\n"}
make_step()

# %% pycharm={"name": "#%%\n"}
make_step()

# %% pycharm={"name": "#%%\n"}
make_step()

# %% pycharm={"name": "#%%\n"}
make_step()

# %% pycharm={"name": "#%%\n"}
make_step()

# %% pycharm={"name": "#%%\n"}
make_step()
