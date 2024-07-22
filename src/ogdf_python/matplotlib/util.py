import warnings

import numpy as np
import sys
from dataclasses import dataclass, asdict
from typing import List, Optional
import collections
import itertools

from matplotlib.collections import PathCollection, Collection
from matplotlib.figure import Figure
from matplotlib.path import Path
from matplotlib.text import Text
from matplotlib.transforms import Affine2D

from ogdf_python.loader import *

__all__ = ["color", "fillPattern", "strokeType", "dPolylineToPath", "dPolylineToPathVertices", "EdgeStyle", "NodeStyle",
           "StyledElementCollection", "get_node_shape", "get_edge_path", "find_closest", "new_figure"]


def color(c):
    if c.alpha() == 255:
        return str(c.toString())
    else:
        return str(c.toString()), c.alpha() / 255


def fillPattern(fp):
    if isinstance(fp, str) and len(fp) == 1:
        fp = ogdf.FillPattern(ord(fp))
    if fp == ogdf.FillPattern.Solid:
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
    else:
        warnings.warn(f"Unknown FillPattern {fp!r}")
        return ""


def strokeType(st):
    if isinstance(st, str) and len(st) == 1:
        st = ogdf.StrokeType(ord(st))
    if st == ogdf.StrokeType.Solid:
        return "solid"
    elif st == ogdf.StrokeType.Dash:
        return "dashed"
    elif st == ogdf.StrokeType.Dot:
        return "dotted"
    elif st == ogdf.StrokeType.Dashdot:
        return "dashdot"
    elif st == ogdf.StrokeType.Dashdotdot:
        return (0, (3, 5, 1, 5, 1, 5))
    elif st == getattr(ogdf.StrokeType, "None"):
        return (0, (0, 10))
    else:
        warnings.warn(f"Unknown StrokeType {st!r}")
        return ""


def dPolylineToPathVertices(poly):
    return [(p.m_x, p.m_y) for p in poly]


def dPolylineToPath(poly, closed=False):
    if closed:
        return Path(dPolylineToPathVertices(poly) + [(0, 0)], closed=True)
    else:
        return Path(dPolylineToPathVertices(poly), closed=False)


FROZEN_DATACLASS = dict(frozen=True)
if sys.version_info >= (3, 10):
    FROZEN_DATACLASS["slots"] = True


@dataclass(**FROZEN_DATACLASS)
class EdgeStyle:
    edgecolor: str
    linestyle: str
    linewidth: float

    def create_text(self, text, x, y):
        return Text(
            x=x, y=y,
            text=text,
            color=self.edgecolor,
            verticalalignment='center', horizontalalignment='center',
            zorder=300,
        )

    def create_collection(self, paths):
        d = {k + 's': v for k, v in self.asdict().items() if v}
        if "edgecolors" in d:
            d["facecolors"] = d["edgecolors"]
        return PathCollection(paths=paths, zorder=100, **d)

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


@dataclass(**FROZEN_DATACLASS)
class NodeStyle(EdgeStyle):
    facecolor: str
    hatch: str
    hatchBgColor: str

    def create_collection(self, paths):
        d = {k + 's': v for k, v in self.asdict().items() if v}
        if "hatchs" in d:
            d["facecolors"] = "none"
            del d["hatchs"]
        d.pop("hatchBgColors", None)
        return PathCollection(paths=paths, zorder=200, **d)

    def create_hatch_collection(self, paths):
        if not self.hatch:
            return None
        return PathCollection(
            paths=paths, zorder=199, hatch=self.hatch,
            edgecolors=self.facecolor, facecolors=self.hatchBgColor)

    @staticmethod
    def dict_from_GA(GA, obj):
        d = EdgeStyle.dict_from_GA(GA, obj)
        d["facecolor"] = color(GA.fillColor[obj])
        d["hatch"] = fillPattern(GA.fillPattern[obj])
        d["hatchBgColor"] = color(GA.fillBgColor[obj])
        return d


@dataclass
class StyledElementCollection:
    # style: EdgeStyle
    elems: List
    paths: List[Path]
    coll: Collection
    hatch_coll: Optional[Collection] = None

    def add_elem(self, elem, path):
        assert len(self.elems) == len(self.paths)
        idx = len(self.elems)
        self.elems.append(elem)
        self.paths.append(path)
        self.set_stale()
        return idx

    def remove_elem(self, idx):
        assert len(self.elems) == len(self.paths)
        assert 0 <= idx < len(self.elems)
        if idx == len(self.elems) - 1:
            self.elems.pop(-1)
            self.paths.pop(-1)
            self.set_stale()
            return None

        last = self.elems[-1]
        self.elems[idx] = self.elems.pop(-1)
        self.paths[idx] = self.paths.pop(-1)
        self.set_stale()
        return last

    def set_stale(self):
        self.coll.stale = True
        if self.hatch_coll:
            self.hatch_coll.stale = True

    def remove(self):
        self.coll.remove()
        if self.hatch_coll:
            self.hatch_coll.remove()


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
            [Path.MOVETO, Path.LINETO, Path.CURVE3, Path.CURVE3, Path.LINETO, Path.CURVE3, Path.CURVE3, Path.LINETO,
             Path.CURVE3, Path.CURVE3, Path.LINETO,
             Path.CURVE3, Path.CURVE3, Path.CLOSEPOLY]
        )
    else:
        poly = ogdf.DPolyline()
        ogdf.python_matplotlib.drawPolygonShape(s, x, y, w, h, poly)
        return dPolylineToPath(poly, closed=True)


def sliding_window(iterable, n):
    iterator = iter(iterable)
    window = collections.deque(itertools.islice(iterator, n - 1), maxlen=n)
    for x in iterator:
        window.append(x)
        yield tuple(window)


def interpolate_curves(path, curviness):
    if not 0 <= curviness <= 0.5:
        raise ValueError(f"invalid curviness {curviness} outside of range [0, 0.5]")
    out_path = np.zeros((len(path) * 3 - 4, 2))
    out_path[0, :] = path[0]
    out_codes = np.full(len(path) * 3 - 4, Path.LINETO)

    for i, (a, b, c) in enumerate(sliding_window(path, 3)):
        i = i * 3
        out_codes[i + 1] = Path.LINETO
        out_path[i + 1, :] = (
            a[0] + (b[0] - a[0]) * (1 - curviness),
            a[1] + (b[1] - a[1]) * (1 - curviness)
        )
        out_codes[i + 2] = Path.CURVE3
        out_codes[i + 3] = Path.CURVE3
        out_path[i + 2, :] = b
        out_path[i + 3, :] = (
            b[0] + (c[0] - b[0]) * curviness,
            b[1] + (c[1] - b[1]) * curviness
        )
    out_path[-1, :] = path[-1]
    out_codes[-1] = Path.LINETO
    return out_path, out_codes


interpolate_curves([(0, 0), (10, 10), (20, 0)], 0)


def get_edge_path(GA, edge, label_pos=ogdf.DPoint(), closed=False, curviness=0):
    label_pos.m_x = (GA.x[edge.source()] + GA.x[edge.target()]) / 2
    label_pos.m_y = (GA.y[edge.source()] + GA.y[edge.target()]) / 2
    src_arr = ogdf.DPolygon() if ogdf.python_matplotlib.isArrowEnabled(GA, edge.adjSource()) else nullptr
    tgt_arr = ogdf.DPolygon() if ogdf.python_matplotlib.isArrowEnabled(GA, edge.adjTarget()) else nullptr
    poly = ogdf.python_matplotlib.drawEdge(edge, GA, label_pos, src_arr, tgt_arr)

    codes = []
    path = []
    if src_arr:
        src_arr_path = dPolylineToPathVertices(src_arr)
        path.append(np.array(src_arr_path))
        codes.append(np.full(len(src_arr_path), Path.LINETO))

    edge_path = np.array(dPolylineToPathVertices(poly))
    edge_codes = np.full(len(edge_path), Path.LINETO)
    if curviness > 0:
        edge_path, edge_codes = interpolate_curves(edge_path, curviness)
    path.append(edge_path)
    codes.append(edge_codes)

    if tgt_arr:
        tgt_arr_path = dPolylineToPathVertices(tgt_arr)
        path.append(np.array(tgt_arr_path))
        codes.append(np.full(len(tgt_arr_path), Path.LINETO))

    codes[0][0] = Path.MOVETO
    if closed:
        path.append(edge_path[::-1])
        codes.append(edge_codes)

    return Path(np.concatenate(path), np.concatenate(codes))


def find_closest(GA, x, y, edge_dist=10):
    p = ogdf.DPoint(x, y)
    n = ogdf.python_matplotlib.findClosestNode(GA, p)
    if n:
        nd = (p - GA.point(n)).norm()
        if (nd <= max(GA.width[n], GA.height[n]) / 2 and
                get_node_shape(GA.x[n], GA.y[n], GA.width[n], GA.height[n], GA.shape[n])
                        .contains_point((x, y), radius=GA.strokeWidth[n] / 2)):
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
    from matplotlib import _pylab_helpers
    with plt.ioff():
        old_fig = None
        manager = _pylab_helpers.Gcf.get_active()
        if manager is not None:
            old_fig = manager.canvas.figure

        fig = plt.figure(num)

        if old_fig is not None:
            plt.figure(old_fig)
    return fig


# ensure that backend is loaded and doesn't reset any configs (esp. is_interactive)
# when being loaded for the first time
import matplotlib.pyplot as plt

plt.close(new_figure())
