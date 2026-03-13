# %%
# %matplotlib widget
from ogdf_python import *

# All currently usable layouts provided by the ogdf:
layouts = {
    "BalloonLayout": "ogdf/misclayout/BalloonLayout.h",
    "BertaultLayout": "ogdf/misclayout/BertaultLayout.h",
    "CircularLayout": "ogdf/misclayout/CircularLayout.h",
    "DavidsonHarelLayout": "ogdf/energybased/DavidsonHarelLayout.h",
    "DTreeMultilevelEmbedder2D": "ogdf/energybased/DTreeMultilevelEmbedder.h",
    "DTreeMultilevelEmbedder3D": "ogdf/energybased/DTreeMultilevelEmbedder.h",
    "FastMultipoleEmbedder": "ogdf/energybased/FastMultipoleEmbedder.h",
    "FastMultipoleMultilevelEmbedder": "ogdf/energybased/FastMultipoleEmbedder.h",
    "FMMMLayout": "ogdf/energybased/FMMMLayout.h",
    "FPPLayout": "ogdf/planarlayout/FPPLayout.h",
    "GEMLayout": "ogdf/energybased/GEMLayout.h",
    "LinearLayout": "ogdf/misclayout/LinearLayout.h",
    "ModularMultilevelMixer": "ogdf/energybased/multilevel_mixer/ModularMultilevelMixer.h",
    "MultilevelLayout": "ogdf/energybased/MultilevelLayout.h",
    "NodeRespecterLayout": "ogdf/energybased/NodeRespecterLayout.h",
    "PivotMDS": "ogdf/energybased/PivotMDS.h",
    "PlanarDrawLayout": "ogdf/planarlayout/PlanarDrawLayout.h",
    "PlanarizationGridLayout": "ogdf/planarity/PlanarizationGridLayout.h",
    "PlanarizationLayout": "ogdf/planarity/PlanarizationLayout.h",
    "PlanarStraightLayout": "ogdf/planarlayout/PlanarStraightLayout.h",
    "RadialTreeLayout": "ogdf/tree/RadialTreeLayout.h",
    "SchnyderLayout": "ogdf/planarlayout/SchnyderLayout.h",
    "SpringEmbedderFRExact": "ogdf/energybased/SpringEmbedderFRExact.h",
    "SpringEmbedderGridVariant": "ogdf/energybased/SpringEmbedderGridVariant.h",
    "SpringEmbedderKK": "ogdf/energybased/SpringEmbedderKK.h",
    "StressMinimization": "ogdf/energybased/StressMinimization.h",
    "SugiyamaLayout": "ogdf/layered/SugiyamaLayout.h",
    "TreeLayout": "ogdf/tree/TreeLayout.h",
    "TutteLayout": "ogdf/energybased/TutteLayout.h",
}

# %%

# Generate some example graph
cppinclude("ogdf/basic/graph_generators/randomized.h")
cppinclude("ogdf/layered/SugiyamaLayout.h")

G = ogdf.Graph()
H = ogdf.Graph()
ogdf.setSeed(1)
ogdf.randomPlanarCNBGraph(H, 20, 40, 3)
G.insert(H)
ogdf.randomPlanarCNBGraph(H, 10, 20, 3)
G.insert(H)
GA = ogdf.GraphAttributes(G, ogdf.GraphAttributes.all)

for n in G.nodes:
    GA.label[n] = "N%s" % n.index()

# %%
import ipywidgets as ipyw
import textwrap
from ogdf_python.matplotlib import MatplotlibGraph

select = ipyw.Dropdown(options=layouts.keys())
widget = MatplotlibGraph(GA)
info = ipyw.HTML()


def set_layout(_):
    info.value = f"Computing..."
    l = select.value
    print(l, layouts[l])
    print(cppinclude(layouts[l]))
    L = getattr(ogdf, l)()
    GA.clearAllBends()
    try:
        L.call(GA)
    except (ogdf.AssertionFailed, TypeError) as e:
        try:
            if "OGDF assertion `isConnected(" in str(e):
                cppinclude("ogdf/packing/ComponentSplitterLayout.h")
                L2 = ogdf.ComponentSplitterLayout()
                L2.setLayoutModule(L)
                L.__python_owns__ = False
                L2.call(GA)
            else:
                raise
        except Exception as e:
            info.value = (
                f"Failed ({textwrap.shorten(str(e), width=100, placeholder='...')})"
            )
            raise
    info.value = f"Success <a href='{L.__doc__}' target='_blank'>(Docs)</a>"
    widget.update_all(GA)
    widget.ax.relim()
    widget.ax.autoscale()
    widget.ax.figure.canvas.draw_idle()


select.observe(set_layout, names="value")
select.value = "SugiyamaLayout"

display(ipyw.VBox([ipyw.HBox([select, info]), widget.ax.figure.canvas]))
