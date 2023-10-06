from dataclasses import dataclass, asdict

from matplotlib.figure import Figure
from matplotlib.path import Path
from matplotlib.transforms import Affine2D

from ogdf_python.loader import *

__all__ = ["color", "fillPattern", "strokeType", "dPolylineToPath", "dPolylineToPathVertices", "EdgeStyle", "NodeStyle", "NodeStyleShape", "get_node_shape", "get_edge_path","find_closest", "new_figure"]


def color(c):
    return str(c.toString())


def fillPattern(fp):
    if not fp:
        return ""
    elif fp == ogdf.FillPattern.Solid:
        return ""
    elif fp == ogdf.FillPattern.Dense1:
        return "O"
    elif fp == ogdf.FillPattern.Dense2:
        return "o"
    elif fp == ogdf.FillPattern.Dense3:
        return "*"
    elif fp == ogdf.FillPattern.Dense4:
        return "."
    elif fp == ogdf.FillPattern.Dense5:
        return "OO"
    elif fp == ogdf.FillPattern.Dense6:
        return "**"
    elif fp == ogdf.FillPattern.Dense7:
        return ".."
    elif fp == ogdf.FillPattern.Horizontal:
        return "-"
    elif fp == ogdf.FillPattern.Vertical:
        return "|"
    elif fp == ogdf.FillPattern.Cross:
        return "+"
    elif fp == ogdf.FillPattern.BackwardDiagonal:
        return "\\"
    elif fp == ogdf.FillPattern.ForwardDiagonal:
        return "/"
    elif fp == ogdf.FillPattern.DiagonalCross:
        return "x"


def strokeType(st):
    if not st:
        return ""
    elif st == ogdf.StrokeType.Solid:
        return "-",
    elif st == ogdf.StrokeType.Dash:
        return "--",
    elif st == ogdf.StrokeType.Dot:
        return ":",
    elif st == ogdf.StrokeType.Dashdot:
        return "-.",
    elif st == ogdf.StrokeType.Dashdotdot:
        return (0, (3, 5, 1, 5, 1, 5)),


def dPolylineToPathVertices(poly):
    return [(p.m_x, p.m_y) for p in poly]


def dPolylineToPath(poly, closed=False):
    if closed:
        return Path(dPolylineToPathVertices(poly) + [(0, 0)], closed=True)
    else:
        return Path(dPolylineToPathVertices(poly), closed=False)


@dataclass(frozen=True, slots=True)
class EdgeStyle:
    edgecolor: str
    linestyle: str
    linewidth: float

    def asdict(self):
        return asdict(self)

    @classmethod
    def from_GA(cls, GA, obj):
        return cls(**cls.dict_from_GA(GA, obj))

    @staticmethod
    def dict_from_GA(GA, obj):
        return dict(
            edgecolor=color(GA.strokeColor[obj]),
            linestyle=strokeType(GA.strokeType[obj]),
            linewidth=GA.strokeWidth[obj],
        )


@dataclass(frozen=True, slots=True)
class NodeStyle(EdgeStyle):
    facecolor: str
    hatch: str

    # TODO fillBgColor

    @staticmethod
    def dict_from_GA(GA, obj):
        d = EdgeStyle.dict_from_GA(GA, obj)
        d["facecolor"] = color(GA.fillColor[obj])
        d["hatch"] = fillPattern(GA.fillPattern[obj])
        return d


@dataclass(frozen=True, slots=True)
class NodeStyleShape(NodeStyle):
    shape: int
    width: float
    height: float

    @staticmethod
    def dict_from_GA(GA, obj):
        d = NodeStyle.dict_from_GA(GA, obj)
        d["shape"] = GA.shape[obj]
        d["width"] = GA.width[obj]
        d["height"] = GA.height[obj]
        return d


def get_node_shape(x, y, w, h, s):
    if s == ogdf.Shape.Ellipse:
        circ = Path.unit_circle()
        trans = Affine2D()
        trans.scale(w, h)
        trans.translate(x, y)
        return circ.transformed(trans)
    elif s == ogdf.Shape.RoundedRect:
        b = min(w, h) * 0.1
        return Path(
            [(x - w / 2, y - h / 2 + b),
             (x - w / 2, y + h / 2 - b),
             (x - w / 2, y + h / 2), (x - w / 2 + b, y + h / 2),
             (x + w / 2 - b, y + h / 2),
             (x + w / 2, y + h / 2), (x + w / 2, y + h / 2 - b),
             (x + w / 2, y - h / 2 + b),
             (x + w / 2, y - h / 2), (x + w / 2 - b, y - h / 2),
             (x - w / 2 + b, y - h / 2),
             (x - w / 2, y - h / 2), (x - w / 2, y - h / 2 + b),
             (0, 0)],
            [Path.MOVETO, Path.LINETO, Path.CURVE3, Path.CURVE3, Path.LINETO, Path.CURVE3, Path.CURVE3, Path.LINETO, Path.CURVE3, Path.CURVE3, Path.LINETO,
             Path.CURVE3, Path.CURVE3, Path.CLOSEPOLY]
        )
    else:
        poly = ogdf.DPolyline()
        ogdf.python_matplotlib.drawPolygonShape(s, x, y, w, h, poly)
        return dPolylineToPath(poly, closed=True)


def get_edge_path(GA, edge, label_pos=ogdf.DPoint(), closed=False):
    label_pos.m_x = (GA.x[edge.source()] + GA.x[edge.target()]) / 2
    label_pos.m_y = (GA.y[edge.source()] + GA.y[edge.target()]) / 2
    src_arr = ogdf.DPolygon() if ogdf.python_matplotlib.isArrowEnabled(GA, edge.adjSource()) else nullptr
    tgt_arr = ogdf.DPolygon() if ogdf.python_matplotlib.isArrowEnabled(GA, edge.adjTarget()) else nullptr
    poly = ogdf.python_matplotlib.drawEdge(edge, GA, label_pos, src_arr, tgt_arr)
    edge_path = dPolylineToPathVertices(poly)
    path = []
    if src_arr:
        path.extend(dPolylineToPathVertices(src_arr))
    path.extend(edge_path)
    if tgt_arr:
        path.extend(dPolylineToPathVertices(tgt_arr))
    if closed:
        path.extend(reversed(edge_path))
    return Path(path, closed=closed)


def find_closest(GA, x, y, edge_dist=10):
    p = ogdf.DPoint(x, y)
    n = ogdf.python_matplotlib.findClosestNode(GA, p)
    if n:
        nd = (p - GA.point(n)).norm()
        if nd <= max(GA.width[n], GA.height[n]) / 2:
            # TODO check that the node shape contains the point
            return n, nd, GA.point(n)
    out = ogdf.DPoint()
    e = ogdf.python_matplotlib.findClosestEdge(GA, p, out)
    if e:
        ed = (p - out).norm()
        if ed <= edge_dist:
            return e, ed, out
    return None, None, None


def new_figure(num=None) -> Figure:
    import matplotlib.pyplot as plt
    with plt.ioff():
        old_fig = plt.gcf()
        fig = plt.figure(num)
        plt.figure(old_fig)
    return fig
