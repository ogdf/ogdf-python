# %%
# %matplotlib widget
from ogdf_python import *

cppinclude("ogdf/basic/graph_generators/randomized.h")
cppinclude("ogdf/basic/simple_graph_alg.h")
cppinclude("ogdf/energybased/FMMMLayout.h")
cppinclude("ogdf/basic/LayoutStatistics.h")

ogdf.setSeed(1234)
G = ogdf.Graph()
GA = ogdf.GraphAttributes(G, ogdf.GraphAttributes.all)
ogdf.randomGraph(G, 20, 50)
ogdf.makeSimpleUndirected(G)
L = ogdf.FMMMLayout()
L.unitEdgeLength(50)
L.call(GA)
for n in G.nodes:
    GA.label[n] = str(n.index())
crossings = ogdf.LayoutStatistics.numberOfCrossings(GA)
print(
    "Total Crossings:", sum(crossings) // 2, " Max Crossings per Edge:", max(crossings)
)
GA

# %%
cppinclude("ogdf/planarity/PlanRep.h")
from ctypes import c_int

PR = ogdf.PlanRep(GA)
print(PR.numberOfCCs())
CC = 0
PR.initCC(CC)

# %%
cppinclude("ogdf/planarity/PlanarizerMixedInsertion.h")
mim = ogdf.PlanarizerMixedInsertion()
count = c_int(0)
result = mim.call(PR, CC, count)
print("Result", result, "Crossings", count, PR.numberOfNodes() - G.numberOfNodes())

# %%
cppinclude("ogdf/orthogonal/OrthoLayout.h")
PRL = ogdf.Layout(PR)
PRA = ogdf.GraphAttributes(PR, ogdf.GraphAttributes.all)
ogdf.OrthoLayout().call(PR, PR.edges[0].adjSource(), PRL)
for n in PR.nodes:
    PRA.x[n] = PRL.x(n)
    PRA.y[n] = PRL.y(n)
    if PR.original(n):
        PRA.label[n] = GA.label[PR.original(n)]
    else:
        PRA.width[n] = 2
        PRA.height[n] = 2
for e in PR.edges:
    PRA.bends[e] = PRL.bends(e)
PRA
