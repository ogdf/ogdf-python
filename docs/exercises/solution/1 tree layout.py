# %%
%matplotlib widget
from ogdf_python import ogdf, cppinclude

cppinclude("ogdf/basic/graph_generators/randomized.h")

G = ogdf.Graph()
ogdf.setSeed(1)
ogdf.randomTree(G, 15)
root = G.nodes[0]
GA = ogdf.GraphAttributes(G, ogdf.GraphAttributes.all)

G

# %%
post = ogdf.NodeArray[int](G, -1)
depth = ogdf.NodeArray[int](G, -1)


def postorder(n, count=0, level=0):
    for adj in n.adjEntries:
        if not adj.isSource():
            continue
        count = postorder(adj.twinNode(), count, level + 1)

    depth[n] = level
    post[n] = count
    return count + 1


postorder(root)

# %%
for n in G.nodes:
    GA.y[n] = depth[n] * 50
    GA.x[n] = post[n] * 50
GA
