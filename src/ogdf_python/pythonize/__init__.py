import re

from ogdf_python.doxygen import pythonize_docstrings, wrap_getattribute
from ogdf_python.pythonize.container import *
from ogdf_python.pythonize.graph_attributes import *
from ogdf_python.pythonize.render import *
from ogdf_python.pythonize.str import *


def pythonize_ogdf(klass, name):
    # print(name, klass)
    pythonize_docstrings(klass, name)

    if name in ("Graph", "ClusterGraph"):
        klass._repr_html_ = GraphAttributes_to_html
    elif name in ("GraphAttributes", "ClusterGraphAttributes"):
        replace_GraphAttributes(klass, name)
        klass._repr_html_ = GraphAttributes_to_html

    # TODO setitem?
    # TODO array slicing
    elif name.startswith("GraphObjectContainer"):
        klass.byid = GraphObjectContainer_byindex
        klass.__getitem__ = iterable_getitem
    elif re.match("S?List(Pure)?", name):
        klass.__getitem__ = iterable_getitem
    elif re.match("List(Const)?(Reverse)?Iterator(Base)?(<.+>)?", name):
        klass.__next__ = advance_iterator
    elif re.match("(Node|Edge|AdjEntry|Cluster|Face)Array", name):
        klass.__iter__ = cpp_iterator
        # klass.__str__ = grapharray_str # TODO there is no generic way to get the key list (yet)

    elif name == "NodeElement":
        klass.__str__ = node_str
        klass.__repr__ = node_repr
    elif name == "EdgeElement":
        klass.__str__ = edge_str
        klass.__repr__ = edge_repr
    elif name == "AdjElement":
        klass.__str__ = adjEntry_str
        klass.__repr__ = adjEntry_repr


cppyy.py.add_pythonization(pythonize_ogdf, "ogdf")
cppyy.py.add_pythonization(pythonize_ogdf, "ogdf::internal")
generate_GA_setters()
wrap_getattribute(cppyy.gbl.ogdf)
