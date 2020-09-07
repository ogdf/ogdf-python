import functools
import re
import tempfile

import cppyy


class GraphAttributesProxy(object):
    def __init__(self, GA, getter, setter):
        self.GA = GA
        self.getter = getter
        self.setter = setter

    def __setitem__(self, key, item):
        return self.setter(self.GA, key, item)

    def __getitem__(self, key):
        return self.getter(self.GA, key)

    def __call__(self, key):
        return self.getter(self.GA, key)


class GraphAttributesDescriptor(object):
    def __init__(self, getter, setter):
        self.getter = getter
        self.setter = setter

    def __get__(self, obj, type=None):
        return GraphAttributesProxy(obj, self.getter, self.setter)


GA_FIELDS = [
    ("x", "ogdf::node", "double"),
    ("y", "ogdf::node", "double"),
    ("z", "ogdf::node", "double"),
    ("xLabel", "ogdf::node", "double"),
    ("yLabel", "ogdf::node", "double"),
    ("zLabel", "ogdf::node", "double"),
    ("width", "ogdf::node", "double"),
    ("height", "ogdf::node", "double"),
    ("shape", "ogdf::node", "ogdf::Shape"),
    ("strokeType", "ogdf::node", "ogdf::StrokeType"),
    ("strokeColor", "ogdf::node", "const ogdf::Color &"),
    ("strokeWidth", "ogdf::node", "float"),
    ("fillPattern", "ogdf::node", "ogdf::FillPattern"),
    ("fillColor", "ogdf::node", "const ogdf::Color &"),
    ("fillBgColor", "ogdf::node", "const ogdf::Color &"),
    ("label", "ogdf::node", "const std::string &"),
    ("templateNode", "ogdf::node", "const std::string &"),
    ("weight", "ogdf::node", "int"),
    ("type", "ogdf::node", "ogdf::Graph::NodeType"),
    ("idNode", "ogdf::node", "int"),
    ("bends", "ogdf::edge", "const ogdf::DPolyline &"),
    ("arrowType", "ogdf::edge", "ogdf::EdgeArrow"),
    ("strokeType", "ogdf::edge", "ogdf::StrokeType"),
    ("strokeColor", "ogdf::edge", "const ogdf::Color &"),
    ("strokeWidth", "ogdf::edge", "float"),
    ("label", "ogdf::edge", "const std::string &"),
    ("intWeight", "ogdf::edge", "int"),
    ("doubleWeight", "ogdf::edge", "double"),
    ("type", "ogdf::edge", "ogdf::Graph::EdgeType"),
    ("subGraphBits", "ogdf::edge", "uint32_t"),
]
CGA_FIELDS = [
    ("x", "ogdf::cluster", "double"),
    ("y", "ogdf::cluster", "double"),
    ("width", "ogdf::cluster", "double"),
    ("height", "ogdf::cluster", "double"),
    ("label", "ogdf::cluster", "const std::string &"),
    ("strokeType", "ogdf::cluster", "ogdf::StrokeType"),
    ("strokeColor", "ogdf::cluster", "const ogdf::Color &"),
    ("strokeWidth", "ogdf::cluster", "float"),
    ("fillPattern", "ogdf::cluster", "ogdf::FillPattern"),
    ("fillColor", "ogdf::cluster", "const ogdf::Color &"),
    ("fillBgColor", "ogdf::cluster", "const ogdf::Color &"),
    ("templateCluster", "ogdf::cluster", "const std::string &"),
]
GA_FIELD_NAMES = set(t[0] for t in GA_FIELDS)
CGA_FIELD_NAMES = set(t[0] for t in GA_FIELDS + CGA_FIELDS)


def generate_GA_setters():
    DEFS = """
#include <ogdf/basic/GraphAttributes.h>
#include <ogdf/cluster/ClusterGraphAttributes.h>

namespace ogdf_pythonization {
    void GraphAttributes_set_directed(ogdf::GraphAttributes &GA, bool v) { GA.directed() = v; }"""
    for name, obj, val in GA_FIELDS:
        DEFS += ("\n\tvoid GraphAttributes_set_{name}(ogdf::GraphAttributes &GA, {obj} o, {val} v) "
                 "{{ GA.{name}(o) = v; }}\n".format(name=name, obj=obj, val=val))
    for name, obj, val in CGA_FIELDS:
        DEFS += ("\n\tvoid GraphAttributes_set_{name}(ogdf::ClusterGraphAttributes &GA, {obj} o, {val} v) "
                 "{{ GA.{name}(o) = v; }}\n".format(name=name, obj=obj, val=val))
    cppyy.cppdef(DEFS + "};")


SVGConf = None


def GraphAttributes_to_html(self):
    global SVGConf
    if SVGConf == None:
        SVGConf = cppyy.gbl.ogdf.GraphIO.SVGSettings()
        SVGConf.margin(50)
        SVGConf.bezierInterpolation(True)
        SVGConf.curviness(0.3)
    with tempfile.NamedTemporaryFile("w+t", suffix=".svg", prefix="ogdf-python-") as f:
        # os = cppyy.gbl.std.ofstream(f.name)
        # cppyy.bind_object(cppyy.addressof(os), "std::basic_ostream<char>")
        cppyy.gbl.ogdf.GraphIO.drawSVG(self, f.name, SVGConf)
        # os.close()
        return f.read()


def replace_GraphAttributes(klass, name):
    if not name.endswith("GraphAttributes"): return
    klass.directed = property(klass.directed, cppyy.gbl.ogdf_pythonization.GraphAttributes_set_directed)
    for field in (CGA_FIELD_NAMES if name.startswith("Cluster") else GA_FIELD_NAMES):
        setattr(klass, field, GraphAttributesDescriptor(
            getattr(klass, field),
            getattr(cppyy.gbl.ogdf_pythonization, "GraphAttributes_set_%s" % field)
        ))
    klass._repr_html_ = GraphAttributes_to_html


generate_GA_setters()
replace_GraphAttributes(cppyy.gbl.ogdf.GraphAttributes, "GraphAttributes")
replace_GraphAttributes(cppyy.gbl.ogdf.ClusterGraphAttributes, "ClusterGraphAttributes")

cppyy.gbl.ogdf.Graph._repr_html_ = GraphAttributes_to_html  # TODO layout
cppyy.gbl.ogdf.ClusterGraph._repr_html_ = GraphAttributes_to_html


def GraphObjectContainer_getitem(self, idx):
    for e in self:
        if e.index() == idx:
            return e
    raise IndexError()


def pythonize_ogdf_internal(klass, name):
    if name.startswith("GraphObjectContainer"):
        klass.__getitem__ = GraphObjectContainer_getitem


cppyy.py.add_pythonization(pythonize_ogdf_internal, "ogdf::internal")


class StreamToStr(object):
    def __init__(self, klass):
        self.klass = klass
        self.old_str = klass.__str__

    def __get__(self, obj, type=None):
        @functools.wraps(self.old_str)
        def to_str():
            try:
                return cppyy.gbl.ogdf_pythonization.to_string(obj)
            except TypeError as e:
                print(e)
                return self.old_str(obj)

        return to_str


def generic_getitem(self, idx):
    # TODO more efficient implementation for random-access, reverse iteration
    for i, e in enumerate(self):
        if i == idx:
            return e
    raise IndexError()


def pythonize_ogdf(klass, name):
    if not isinstance(klass.__str__, StreamToStr):
        klass.__str__ = StreamToStr(klass)
    if re.match("List(Const)?(Reverse)?Iterator(Base)?(<.+>)?", name):
        def advance(self):
            if not self.valid():
                raise StopIteration()
            val = self.__deref__()
            self.__preinc__()
            return val

        klass.__next__ = advance
    if re.match("S?List(Pure)?", name):
        klass.__getitem__ = generic_getitem
        # TODO setitem?


cppyy.py.add_pythonization(pythonize_ogdf, "ogdf")
