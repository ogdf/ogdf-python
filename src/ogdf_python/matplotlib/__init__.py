from importlib.resources import *

from ogdf_python.loader import *
from ogdf_python.matplotlib.gui import GraphEditorLayout
from ogdf_python.matplotlib.util import *
from ogdf_python.matplotlib.widget import MatplotlibGraph, MatplotlibGraphEditor

__all__ = ["MatplotlibGraph", "MatplotlibGraphEditor", "GraphEditorLayout"]

with as_file(files(__package__).joinpath("rendering.h")) as header:
    cppinclude(header)


def repr_mimebundle_GraphAttributes(self, *args, **kwargs):
    from IPython.core.interactiveshell import InteractiveShell

    if not InteractiveShell.initialized():
        return {"text/plain": repr(self)}, {}

    from ogdf_python.matplotlib.widget import MatplotlibGraph
    fig = new_figure()
    ax = fig.subplots()
    fig.graph = MatplotlibGraph(self, ax)
    data, meta = InteractiveShell.instance().display_formatter.format(fig.canvas, *args, **kwargs)
    if not data:
        # object handled itself through display, don't proceed
        return data, meta
    else:
        data["text/plain"] = repr(self)
        return data, meta


def repr_mimebundle_Graph(self, *args, **kwargs):
    from ogdf_python.pythonize import renderGraph
    return repr_mimebundle_GraphAttributes(renderGraph(self), *args, **kwargs)


def repr_mimebundle_ClusterGraph(self, *args, **kwargs):
    from ogdf_python.pythonize import renderClusterGraph
    return repr_mimebundle_GraphAttributes(renderClusterGraph(self), *args, **kwargs)


ogdf.GraphAttributes._repr_mimebundle_ = repr_mimebundle_GraphAttributes
ogdf.Graph._repr_mimebundle_ = repr_mimebundle_Graph
ogdf.ClusterGraphAttributes._repr_mimebundle_ = repr_mimebundle_GraphAttributes
ogdf.ClusterGraph._repr_mimebundle_ = repr_mimebundle_ClusterGraph
