# %%
%matplotlib widget

import os
import re
from collections import defaultdict

from ogdf_python import *

ogdf.LayoutStandards.setDefaultEdgeArrow(ogdf.EdgeArrow.Last)

# %%
DIR = get_base_include_path()

HEADERS = [
    os.path.relpath(os.path.join(root, file), DIR)
    for root, dirs, files in os.walk(DIR)
    for file in files
]
CGA = CG = G = None
G = ogdf.Graph()
CG = ogdf.ClusterGraph(G)
CG.setUpdateDepth(True)
CGA = ogdf.ClusterGraphAttributes(CG, ogdf.ClusterGraphAttributes.all)

NODES = {h: G.newNode() for h in HEADERS}
UNKNOWN = defaultdict(list)
CLUSTERS = {}

for header, node in NODES.items():
    CGA.label[node] = header
    CGA.width[node] = len(header) * 5

    parents = os.path.dirname(header).split(os.sep)
    cluster_path = cluster = None
    for i in range(1, len(parents) + 1):
        cluster_path = os.sep.join(parents[:i])
        if cluster_path not in CLUSTERS:
            cluster = CLUSTERS[cluster_path] = CG.createEmptyCluster(cluster or nullptr)
            CGA.label[cluster] = cluster_path
            CGA.strokeType[cluster] = ogdf.StrokeType.Dash
        else:
            cluster = CLUSTERS[cluster_path]
    if cluster is not None:
        CG.reassignNode(node, cluster)

    with open(os.path.join(DIR, header)) as f:
        for match in re.finditer('#include\s+(["<])(.*)([">])', f.read()):
            include = match.group(2)
            include_rel = os.path.join(os.path.dirname(header), include)
            if include in NODES:
                e = G.newEdge(node, NODES[include])
            elif include_rel in NODES and match.group(1) == '"':
                e = G.newEdge(node, NODES[include_rel])
            else:
                UNKNOWN[match.group(1) + include + match.group(3)].append(header)

print(G.numberOfNodes(), G.numberOfEdges(), CG.numberOfClusters(), CG.treeDepth())

# %% pycharm={"name": "#%%\n"}
cppinclude("ogdf/layered/SugiyamaLayout.h")
cppinclude("ogdf/layered/MedianHeuristic.h")
cppinclude("ogdf/layered/OptimalHierarchyClusterLayout.h")
cppinclude("ogdf/layered/OptimalRanking.h")

SL = ogdf.SugiyamaLayout()
r = ogdf.OptimalRanking()
r.__python_owns__ = False
SL.setRanking(r)
h = ogdf.MedianHeuristic()
h.__python_owns__ = False
SL.setCrossMin(h)

ohl = ogdf.OptimalHierarchyClusterLayout()
ohl.__python_owns__ = False
ohl.layerDistance(30.0)
ohl.nodeDistance(100.0)
ohl.weightBalancing(0.8)
SL.setClusterLayout(ohl)

SL.call(CGA)
for name, node in NODES.items():
    CGA.width[node] = len(name) * 5
CGA.updateClusterPositions()
ogdf.GraphIO.drawSVG(CGA, "ogdf-includes.svg")
# ogdf.GraphIO.write(CGA, "ogdf-includes.gml")
CGA

# %%
for e in G.edges:
    print(CGA.arrowType(e))
