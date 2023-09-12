from importlib.resources import *

from ogdf_python.loader import *
from ogdf_python.matplotlib.gui import GraphEditorLayout
from ogdf_python.matplotlib.util import *
from ogdf_python.matplotlib.widget import MatplotlibGraph, MatplotlibGraphEditor

__all__ = ["MatplotlibGraph", "MatplotlibGraphEditor", "GraphEditorLayout"]

with as_file(files(__package__).joinpath("rendering.h")) as header:
    cppinclude(header)


# cppinclude("Python.h")


def display_GraphAttributes(self):
    from IPython.display import display
    from ogdf_python.matplotlib.widget import MatplotlibGraph
    fig = new_figure()
    ax = fig.subplots()
    fig.graph = MatplotlibGraph(self, ax)
    display(fig.canvas)
    return None


def display_Graph(self):
    from ogdf_python.pythonize import renderGraph
    return display_GraphAttributes(renderGraph(self))


def display_ClusterGraph(self):
    from ogdf_python.pythonize import renderClusterGraph
    return display_GraphAttributes(renderClusterGraph(self))


ogdf.GraphAttributes._ipython_display_ = display_GraphAttributes
ogdf.Graph._ipython_display_ = display_Graph
ogdf.ClusterGraphAttributes._ipython_display_ = display_GraphAttributes
ogdf.ClusterGraph._ipython_display_ = display_ClusterGraph
