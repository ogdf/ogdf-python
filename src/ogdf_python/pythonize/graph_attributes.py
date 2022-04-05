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

    def __call__(self, *args, **kwargs):
        return self.getter(self.GA, *args, **kwargs)


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
CGA_FIELD_NAMES = set(t[0] for t in CGA_FIELDS)


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


def replace_GraphAttributes(klass, name):
    klass.directed = property(klass.directed, cppyy.gbl.ogdf_pythonization.GraphAttributes_set_directed)
    for field in (CGA_FIELD_NAMES if name.startswith("Cluster") else GA_FIELD_NAMES):
        setattr(klass, field, GraphAttributesDescriptor(
            getattr(klass, field),
            getattr(cppyy.gbl.ogdf_pythonization, "GraphAttributes_set_%s" % field)
        ))