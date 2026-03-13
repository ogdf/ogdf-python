# %%
# %matplotlib widget
from ogdf_python import ogdf

# Let's start with our planar graph from last lession...

G = ogdf.Graph()
N = [G.newNode() for _ in range(4)]
for u in N:
    for v in N:
        if u.index() < v.index():
            G.newEdge(u, v)
G.reverseAdjEdges(N[1])
G.reverseAdjEdges(N[3])

G

# %%
# To create a drawing of G, we have to store some drawing-related attributes about it
GA = ogdf.GraphAttributes(G, ogdf.GraphAttributes.all)
# GraphAttributes.all means that all available attributes will be enabled, more on that later

n = N[0]  # lets put this node at some coordinate and give it a name
GA.x[n] = 100
GA.y[n] = 100
GA.label[n] = "n0"

GA

# %%
# the other nodes are still missing coordinates, let's fix that!
GA.x[N[1]], GA.y[N[1]] = 0, 0
GA.x[N[2]], GA.y[N[2]] = 100, 200
GA.x[N[3]], GA.y[N[3]] = 0, 200

for n in N:
    GA.label[n] = str(n.index())

GA

# %%
# Note: the coordinates in GA do not need to correlate with the current combinatorial embedding!
print("Planar?", G.representsCombEmbedding())  # G is planar while GA is not!
for n in G.nodes:
    print(n)
# check where the orders differ!

# %%
# one graph can have multiple drawings by having multiple instances of GraphAttributes
GA2 = ogdf.GraphAttributes(
    GA
)  # creates a copy of GA so that we only have to fix a few coordinates
GA2.x[N[1]], GA2.y[N[1]] = 100, 0
GA2.x[N[2]], GA2.y[N[2]] = 200, 200
GA2

# %%
GA  # the old, non-planar instance is still there, too!

# %%
help(GA)  # GA has some nice function for modifying the drawings

# %% [markdown]
# The following flags can be passed as second constructor argument to only enable certain attributes:
#
# | Bitmask Flag      | Attributes                                                    |
# |:------------------|:--------------------------------------------------------------|
# | nodeGraphics      | x, y, width, height, shape                                    |
# | edgeGraphics      | bends                                                         |
# | edgeStyle         | strokeColor, strokeType, strokeWidth, strokeColor, strokeType |
# | nodeStyle         | strokeWidth, fillPattern, fillColor, fillBgColor              |
# | edgeLabel         | label                                                         |
# | nodeLabel         | label                                                         |
# | edgeIntWeight     | intWeight                                                     |
# | edgeDoubleWeight  | doubleWeight                                                  |
# | nodeWeight        | weight                                                        |
# | edgeType          | type                                                          |
# | nodeType          | type                                                          |
# | nodeId            | idNode                                                        |
# | edgeArrow         | arrowType                                                     |
# | nodeTemplate      | templateNode                                                  |
# | threeD            | z                                                             |
# | nodeLabelPosition | xLabel, yLabel, zLabel                                        |
#
# The default `ogdf.GraphAttributes.nodeGraphics | ogdf.GraphAttributes.edgeGraphics` thus enables `GA.x, GA.y, GA.width, GA.height, GA.shape` and `GA.bends` (a list of bend point coordinates for edges), but not `GA.label` (which can stores labels for edges and nodes at the same time). Passing `ogdf.GraphAttributes.all` enables all attributes at the cost of a little more RAM.

# %%
# using GraphIO we can now dump a computer-readable representation of the graph and drawing
ogdf.GraphIO.write(GA, "test.gml")
# to only dump the graph structure without a drawing, you can also pass `G` instead of `GA`

# GraphIO can also write human-readable SVG images
ogdf.GraphIO.write(GA, "test.svg")

# and it can also read back the computer-readable data
G_r = ogdf.Graph()
GA_r = ogdf.GraphAttributes(G_r, ogdf.GraphAttributes.all)
ogdf.GraphIO.read(GA_r, G_r, "test.gml")
GA_r  # see, that's the same drawing!
