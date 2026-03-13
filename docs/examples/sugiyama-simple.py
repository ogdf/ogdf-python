# %%
%matplotlib widget
# uncomment if you didn't install OGDF globally:
# # %env OGDF_BUILD_DIR=~/ogdf/build-debug
from ogdf_python import *

cppinclude("ogdf/basic/graph_generators/randomized.h")
cppinclude("ogdf/layered/SugiyamaLayout.h")

G = ogdf.Graph()
ogdf.setSeed(1)
ogdf.randomPlanarTriconnectedGraph(G, 20, 40)
GA = ogdf.GraphAttributes(G, ogdf.GraphAttributes.all)

for n in G.nodes:
    GA.label[n] = "N%s" % n.index()

SL = ogdf.SugiyamaLayout()
SL.call(GA)
ogdf.GraphIO.drawSVG(GA, "sugiyama-simple.svg")
GA
