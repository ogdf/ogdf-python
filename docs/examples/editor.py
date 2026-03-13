# %%
# %matplotlib widget
from ogdf_python import *
from ogdf_python.matplotlib import *
import matplotlib.pyplot as plt

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

# %%
GE = GraphEditorLayout(GA)
display(GE)
# click so select a node or edge
# [del] deletes the selected object
# [ctrl]+click on a node while another node is selected adds an edge
# double click on the background adds a node
