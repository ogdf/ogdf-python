import re

from ogdf_python.doxygen import pythonize_docstrings, wrap_getattribute
from ogdf_python.pythonize.container import *
from ogdf_python.pythonize.graph_attributes import *
from ogdf_python.pythonize.render import *
from ogdf_python.pythonize.string import *


def pythonize_ogdf(klass, name):
    # print(name, klass)
    try:
        pythonize_docstrings(klass, name)
    except Exception:
        pass  # we ignore if updating the docs fails

    if name == "Graph":
        klass._repr_svg_ = Graph_to_svg
    elif name == "ClusterGraph":
        klass._repr_svg_ = ClusterGraph_to_svg
    elif name in ("GraphAttributes", "ClusterGraphAttributes"):
        replace_GraphAttributes(klass, name)
        klass._repr_svg_ = GraphAttributes_to_svg

    # TODO setitem?
    # TODO array slicing
    elif name.startswith("GraphObjectContainer"):
        klass.byid = GraphObjectContainer_byindex
        klass.__getitem__ = iterable_getitem
        klass.__str__ = lambda self: "[%s]" % ", ".join(str(i) for i in self)
        klass.__repr__ = lambda self: "%s([%s])" % (type(self).__name__, ", ".join(repr(i) for i in self))
    elif re.fullmatch("S?List(Pure)?(<.+>)?", name):
        klass.__getitem__ = iterable_getitem
        klass.__str__ = lambda self: "[%s]" % ", ".join(str(i) for i in self)
        klass.__repr__ = lambda self: "%s([%s])" % (type(self).__name__, ", ".join(repr(i) for i in self))
    elif re.fullmatch("List(Const)?(Reverse)?Iterator(Base)?(<.+>)?", name):
        klass.__next__ = advance_iterator
    elif re.fullmatch("(Node|Edge|AdjEntry|Cluster|Face)Array(<.+>)?", name):
        klass.__iter__ = cpp_iterator
        klass.keys = ArrayKeys[name.partition("Array")[0]]
        klass.asdict = lambda self: {k: self[k] for k in self.keys()}
        klass.__str__ = lambda self: str(self.asdict())
        klass.__repr__ = lambda self: "%s(%r)" % (type(self).__name__, self.asdict())
    # TODO NodeSet et al.

    elif name == "NodeElement":
        klass.__str__ = node_str
        klass.__repr__ = node_repr
    elif name == "EdgeElement":
        klass.__str__ = edge_str
        klass.__repr__ = edge_repr
    elif name == "AdjElement":
        klass.__str__ = adjEntry_str
        klass.__repr__ = adjEntry_repr

    elif name == "Color":
        klass.__str__ = lambda self: self.toString().decode("ascii")
        klass.__repr__ = lambda self: "ogdf.Color(%r)" % str(self)

    elif name == "GraphIO":
        for key, func in klass.__dict__.items():
            if key.startswith(("read", "write", "draw")):
                setattr(klass, key, wrap_GraphIO(func))


cppyy.py.add_pythonization(pythonize_ogdf, "ogdf")
cppyy.py.add_pythonization(pythonize_ogdf, "ogdf::internal")
generate_GA_setters()
wrap_getattribute(cppyy.gbl.ogdf)
