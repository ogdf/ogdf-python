from importlib.resources import *

from ogdf_python.loader import *
from ogdf_python.matplotlib.gui import GraphEditorLayout
from ogdf_python.matplotlib.util import *
from ogdf_python.matplotlib.widget import MatplotlibGraph, MatplotlibGraphEditor

__all__ = ["MatplotlibGraph", "MatplotlibGraphEditor", "GraphEditorLayout"]

with as_file(files(__package__).joinpath("rendering.h")) as header:
    cppinclude(header)
cppinclude("Python.h")


def display_GraphAttributes(self):
    from IPython.display import display
    from ogdf_python.matplotlib.widget import MatplotlibGraph
    fig = new_figure()
    ax = fig.subplots()
    fig.graph = MatplotlibGraph(self, ax)
    display(fig.canvas)
    return None


ogdf.GraphAttributes._ipython_display_ = display_GraphAttributes
