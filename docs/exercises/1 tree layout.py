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
depth = ogdf.NodeArray[int](G, -1)


# TODO fill in the dots, possibly making changes to the surrounding code
def postorder(n, level=0): ...


postorder(root)

# %%
for n in G.nodes:
    GA.y[n] = depth[n] * 50  # TODO first, try to calculate the depth
    GA.x[n] = 0  # TODO second, update this to the postorder index
GA
