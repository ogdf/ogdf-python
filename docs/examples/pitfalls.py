# %%
# uncomment if you didn't set this globally:
# # %env OGDF_BUILD_DIR=~/ogdf/build-debug
from ogdf_python import ogdf, cppinclude

# %%
cppinclude("ogdf/layered/SugiyamaLayout.h")
cppinclude("ogdf/layered/MedianHeuristic.h")
cppinclude("ogdf/layered/OptimalHierarchyLayout.h")
cppinclude("ogdf/layered/OptimalRanking.h")

SL = ogdf.SugiyamaLayout()
r = ogdf.OptimalRanking()
r.__python_owns__ = (
    False  # ogdf modules take ownership of objects, conflicting with cppyy clean-up
)
SL.setRanking(r)
h = ogdf.MedianHeuristic()
h.__python_owns__ = False
SL.setCrossMin(h)

ohl = ogdf.OptimalHierarchyLayout()
ohl.__python_owns__ = False
ohl.layerDistance(30.0)
ohl.nodeDistance(25.0)
ohl.weightBalancing(0.8)
SL.setLayout(ohl)

# %%
for i in range(5):
    CGA = CG = G = (
        None  # deletion order is important when overwriting parents of dependant objects
    )
    G = ogdf.Graph()
    CG = ogdf.ClusterGraph(G)
    CGA = ogdf.ClusterGraphAttributes(CG, ogdf.ClusterGraphAttributes.all)
