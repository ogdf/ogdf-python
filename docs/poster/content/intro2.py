from ogdf_python import *

cppinclude("ogdf/basic/graph_generators.h")
cppinclude("ogdf/layered/SugiyamaLayout.h")

G = ogdf.Graph()
GA = ogdf.GraphAttributes(G)
ogdf.randomPlanarTriconnectedGraph(G, 10, 20)

for n in G.nodes:
    GA.label[n] = "N%s" % n.index()

SL = ogdf.SugiyamaLayout()
SL.call(GA)
GA # display inline!