# %%
# %matplotlib widget
from ogdf_python import ogdf, cppinclude

# Let's start out with some bigger graph...

cppinclude(
    "ogdf/basic/graph_generators/randomized.h"
)  # provides randomPlanarTriconnectedGraph

G = ogdf.Graph()
ogdf.setSeed(1)
ogdf.randomPlanarTriconnectedGraph(G, 20, 40)
GA = ogdf.GraphAttributes(G, ogdf.GraphAttributes.all)

G

# %% [markdown]
# OGDF has a lot of automated layout algorithms built-in, check the "Inheritance diagram for ogdf::LayoutModule" [here](https://ogdf.github.io/doc/ogdf/classogdf_1_1_layout_module.html) to get an overview.
#
# Here are also some examples:

# %%
cppinclude("ogdf/layered/SugiyamaLayout.h")

L = ogdf.SugiyamaLayout()
L.call(GA)

GA

# %%
cppinclude("ogdf/planarlayout/SchnyderLayout.h")

# not every layout respects planarity or the implied combinatorial embedd
L2 = ogdf.SchnyderLayout()
L2.call(GA)  # use callFixEmbed if G is already embedded planarly

GA

# %%
cppinclude("ogdf/energybased/SpringEmbedderFRExact.h")

L3 = ogdf.SpringEmbedderFRExact()  # FR = Fruchterman-Reingold
L3.idealEdgeLength(150)  # some LayoutModules have further configuration parameters
# check their docs to see what you can tweak
L3.call(GA)

GA
