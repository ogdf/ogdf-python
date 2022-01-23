import functools
import re
import tempfile
import os
import json
import uuid

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


def color_to_dict(color):
    color = {"r": color.red(),
             "g": color.green(),
             "b": color.blue(),
             "a": color.alpha()}
    return color


def node_to_dict(ga, node):
    return {"id": str(node.index()),
            "name": str(ga.label(node)),
            "x": int(ga.x(node) + 0.5),
            "y": int(ga.y(node) + 0.5),
            "shape": ga.shape(node),
            "fillColor": color_to_dict(ga.fillColor(node)),
            "strokeColor": color_to_dict(ga.strokeColor(node)),
            "strokeWidth": ga.strokeWidth(node),
            "nodeWidth": ga.width(node),
            "nodeHeight": ga.height(node)}


def link_to_dict(ga, link):
    bends = []
    for i, point in enumerate(ga.bends(link)):
        bends.append([int(point.m_x + 0.5), int(point.m_y + 0.5)])

    link_dict = {"id": str(link.index()),
                 "label": str(ga.label(link)),
                 "source": str(link.source().index()),
                 "target": str(link.target().index()),
                 "t_shape": ga.shape(link.target()),
                 "strokeColor": color_to_dict(ga.strokeColor(link)),
                 "strokeWidth": ga.strokeWidth(link),
                 "sx": int(ga.x(link.source()) + 0.5),
                 "sy": int(ga.y(link.source()) + 0.5),
                 "tx": int(ga.x(link.target()) + 0.5),
                 "ty": int(ga.y(link.target()) + 0.5),
                 "arrow": ga.arrowType(link) == 1,
                 "bends": bends}

    if len(bends) > 0:
        link_dict["label_x"] = bends[0][0]
        link_dict["label_y"] = bends[0][1]
    else:
        link_dict["label_x"] = (link_dict["sx"] + link_dict["tx"]) / 2
        link_dict["label_y"] = (link_dict["sy"] + link_dict["ty"]) / 2

    return link_dict


def GraphAttributes_to_html(self):
    # global SVGConf
    # if SVGConf == None:
    #     SVGConf = cppyy.gbl.ogdf.GraphIO.SVGSettings()
    #     SVGConf.margin(50)
    #     SVGConf.bezierInterpolation(True)
    #     SVGConf.curviness(0.3)
    #
    # with tempfile.NamedTemporaryFile("w+t", suffix=".svg", prefix="ogdf-python-") as f:
    #     cppyy.gbl.ogdf.GraphIO.drawSVG(self, f.name, SVGConf)
    #     data = f.read()
    #     data = data.replace('<?xml version="1.0"?>', '')
    #     return data

    if isinstance(self, cppyy.gbl.ogdf.Graph):
        nodes_data = []
        for node in self.nodes:
            nodes_data.append({"id": str(node.index()), "name": str(node.index())})

        links_data = []
        for edge in self.edges:
            links_data.append({"source": str(edge.source().index()), "target": str(edge.target().index())})

        return export_html('basicGraphRepresentation.html', nodes_data, links_data, True)

    if isinstance(self, cppyy.gbl.ogdf.GraphAttributes):
        nodes_data = []
        for node in self.constGraph().nodes:
            nodes_data.append(node_to_dict(self, node))

        links_data = []
        for link in self.constGraph().edges:
            links_data.append(link_to_dict(self, link))

        return export_html('basicGraphRepresentation.html', nodes_data, links_data, False)


cppyy.gbl.ogdf.Graph._repr_html_ = GraphAttributes_to_html
cppyy.gbl.ogdf.GraphAttributes._repr_html_ = GraphAttributes_to_html
cppyy.gbl.ogdf.ClusterGraph._repr_html_ = GraphAttributes_to_html
cppyy.gbl.ogdf.ClusterGraphAttributes._repr_html_ = GraphAttributes_to_html


def export_html(filename, nodes_data, links_data, force_directed):
    __location__ = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))

    with open(os.path.join(__location__, filename), 'r') as file:
        data = file.read()
        data = data.replace("let nodes_data = []", "let nodes_data = " + json.dumps(nodes_data))
        data = data.replace("let links_data = []", "let links_data = " + json.dumps(links_data))
        # the G is needed because CSS3 selector doesnt support ID selectors that start with a digit
        data = data.replace("placeholderId", 'G' + uuid.uuid4().hex)
        if not force_directed:
            data = data.replace("let forceDirected = true;", "let forceDirected = false;")
        return data


def replace_GraphAttributes(klass, name):
    if not name.endswith("GraphAttributes"): return
    klass.directed = property(klass.directed, cppyy.gbl.ogdf_pythonization.GraphAttributes_set_directed)
    for field in (CGA_FIELD_NAMES if name.startswith("Cluster") else GA_FIELD_NAMES):
        setattr(klass, field, GraphAttributesDescriptor(
            getattr(klass, field),
            getattr(cppyy.gbl.ogdf_pythonization, "GraphAttributes_set_%s" % field)
        ))


generate_GA_setters()
replace_GraphAttributes(cppyy.gbl.ogdf.GraphAttributes, "GraphAttributes")
replace_GraphAttributes(cppyy.gbl.ogdf.ClusterGraphAttributes, "ClusterGraphAttributes")


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
