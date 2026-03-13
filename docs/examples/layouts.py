# %%
# %matplotlib widget
from ogdf_python import *

# All currently usable layouts provided by the ogdf:
layouts = {
    "BalloonLayout": "ogdf/misclayout/BalloonLayout.h",
    "BertaultLayout": "ogdf/misclayout/BertaultLayout.h",
    "CircularLayout": "ogdf/misclayout/CircularLayout.h",
    #    'ComponentSplitterLayout': 'ogdf/packing/ComponentSplitterLayout.h',
    "DavidsonHarelLayout": "ogdf/energybased/DavidsonHarelLayout.h",
    "DominanceLayout": "ogdf/upward/DominanceLayout.h",  # fails
    "DTreeMultilevelEmbedder2D": "ogdf/energybased/DTreeMultilevelEmbedder.h",
    "DTreeMultilevelEmbedder3D": "ogdf/energybased/DTreeMultilevelEmbedder.h",
    "FastMultipoleEmbedder": "ogdf/energybased/FastMultipoleEmbedder.h",
    "FastMultipoleMultilevelEmbedder": "ogdf/energybased/FastMultipoleEmbedder.h",
    "FMMMLayout": "ogdf/energybased/FMMMLayout.h",
    #    'ForceLayoutModule': 'ogdf/energybased/ForceLayoutModule.h',
    "FPPLayout": "ogdf/planarlayout/FPPLayout.h",
    "GEMLayout": "ogdf/energybased/GEMLayout.h",
    #    'GridLayoutModule': 'ogdf/planarlayout/GridLayoutModule.h',
    "LinearLayout": "ogdf/misclayout/LinearLayout.h",
    "MixedModelLayout": "ogdf/planarlayout/MixedModelLayout.h",  # fails
    "ModularMultilevelMixer": "ogdf/energybased/multilevel_mixer/ModularMultilevelMixer.h",
    "MultilevelLayout": "ogdf/energybased/MultilevelLayout.h",
    #    'MultilevelLayoutModule': 'ogdf/energybased/multilevel_mixer/MultilevelLayoutModule.h',
    "NodeRespecterLayout": "ogdf/energybased/NodeRespecterLayout.h",
    "PivotMDS": "ogdf/energybased/PivotMDS.h",
    "PlanarDrawLayout": "ogdf/planarlayout/PlanarDrawLayout.h",
    "PlanarizationGridLayout": "ogdf/planarity/PlanarizationGridLayout.h",
    "PlanarizationLayout": "ogdf/planarity/PlanarizationLayout.h",
    "PlanarStraightLayout": "ogdf/planarlayout/PlanarStraightLayout.h",
    #    'PreprocessorLayout': 'ogdf/basic/PreprocessorLayout.h',
    #    'ProcrustesSubLayout': 'ogdf/misclayout/ProcrustesSubLayout.h',
    "RadialTreeLayout": "ogdf/tree/RadialTreeLayout.h",
    #    'ScalingLayout': 'ogdf/energybased/multilevel_mixer/ScalingLayout.h',
    "SchnyderLayout": "ogdf/planarlayout/SchnyderLayout.h",
    #    'SimpleCCPacker': 'ogdf/packing/SimpleCCPacker.h',
    #    'spring_embedder.SpringEmbedderBase': 'ogdf/energybased/spring_embedder/SpringEmbedderBase.h',
    "SpringEmbedderFRExact": "ogdf/energybased/SpringEmbedderFRExact.h",
    "SpringEmbedderGridVariant": "ogdf/energybased/SpringEmbedderGridVariant.h",
    "SpringEmbedderKK": "ogdf/energybased/SpringEmbedderKK.h",
    "StressMinimization": "ogdf/energybased/StressMinimization.h",
    "SugiyamaLayout": "ogdf/layered/SugiyamaLayout.h",
    "TreeLayout": "ogdf/tree/TreeLayout.h",
    "TutteLayout": "ogdf/energybased/TutteLayout.h",
    "UpwardPlanarizationLayout": "ogdf/upward/UpwardPlanarizationLayout.h",  # fails
    "VisibilityLayout": "ogdf/upward/VisibilityLayout.h",  # fails
}

# %%
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

SL = ogdf.SugiyamaLayout()
SL.call(GA)
# GA

# %%
import ipywidgets as ipyw
import textwrap

select = ipyw.Dropdown(options=layouts.keys(), value="SugiyamaLayout")
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

display(ipyw.VBox([ipyw.HBox([select, info]), widget.ax.figure.canvas]))

# %%

# TutteLayout requires the graph to be triconnected
cppinclude("ogdf/energybased/TutteLayout.h")
cppinclude("ogdf/basic/simple_graph_alg.h")
cppinclude("ogdf/basic/extended_graph_alg.h")
L = ogdf.TutteLayout()
GC = ogdf.GraphCopy(G)
GCA = ogdf.GraphAttributes(GC, ogdf.GraphAttributes.all)
ogdf.makeConnected(GC)
ogdf.planarEmbed(GC)
ogdf.triangulate(GC)
L.call(GCA)
# GCA.transferToOriginal(GA) # would overwrite the default layout from above
GCA
