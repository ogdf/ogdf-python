import numpy as np
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from matplotlib.text import Text

from ogdf_python.loader import *
from ogdf_python.matplotlib.util import *


class NodeArtist(PathPatch):
    def __init__(self, node, GA, **kwargs):
        self.node = n = node
        attrs = self.calc_attributes(GA)
        attrs.update(**kwargs)
        path = get_node_shape(GA.x[n], GA.y[n], GA.width[n], GA.height[n], GA.shape[n])
        super().__init__(path, **attrs)
        # TODO use collection for nodes with the same shape?

        self.label = Text(
            x=GA.x[n], y=GA.y[n],
            # xy=(GA.x[self.node],GA.y[self.node]),
            # xytext=(GA.xLabel[self.node],GA.yLabel[self.node]),
            text=GA.label[n],
            color=color(GA.strokeColor[n]),
            verticalalignment='center', horizontalalignment='center',
            zorder=300,
        )
        # bbox = self.label.get_window_extent() # TODO scale

    def remove(self):
        self.label.remove()
        super().remove()

    def update_attributes(self, GA):
        attrs = self.calc_attributes(GA)
        n = self.node
        path = get_node_shape(GA.x[n], GA.y[n], GA.width[n], GA.height[n], GA.shape[n])
        self.set(**attrs, path=path)
        self.label.set(
            x=GA.x[n], y=GA.y[n],
            text=GA.label[n],
            color=color(GA.strokeColor[n]),
        )

    def calc_attributes(self, GA):
        d = NodeStyle.dict_from_GA(GA, self.node)
        d["fill"] = True
        d["zorder"] = 200
        d["picker"] = True
        return d


class EdgeArtist(PathPatch):
    PICK_DISTANCE = 10

    def __init__(self, edge, GA, **kwargs):
        self.edge = edge
        attrs = self.calc_attributes(GA)
        attrs.update(**kwargs)

        # TODO use same path only with translations for arrows
        arr_attrs = self.calc_arrow_attributes(GA)
        self.src_arr = PathPatch(Path([(0, 0)]), **arr_attrs)
        self.tgt_arr = PathPatch(Path([(0, 0)]), **arr_attrs)

        super().__init__(self.calc_path(GA), **attrs)

        self.label = Text(
            x=self.label_pos.m_x, y=self.label_pos.m_y,
            text=GA.label[self.edge],
            color=color(GA.strokeColor[self.edge]),
            verticalalignment='center', horizontalalignment='center',
            zorder=300,
        )  # TODO set background color

    def remove(self):
        self.src_arr.remove()
        self.tgt_arr.remove()
        self.label.remove()
        super().remove()

    def update_attributes(self, GA):
        attrs = self.calc_attributes(GA)
        arr_attrs = self.calc_arrow_attributes(GA)
        path = self.calc_path(GA)
        self.set(**attrs, path=path)
        self.src_arr.set(**arr_attrs)
        self.tgt_arr.set(**arr_attrs)
        self.label.set(
            x=self.label_pos.m_x, y=self.label_pos.m_y,
            text=GA.label[self.edge],
            color=color(GA.strokeColor[self.edge]),
        )

    def calc_attributes(self, GA):
        d = EdgeStyle.dict_from_GA(GA, self.edge)
        d["fill"] = False
        d["zorder"] = 100
        d["picker"] = self._should_pick
        return d

    def calc_arrow_attributes(self, GA):
        d = EdgeStyle.dict_from_GA(GA, self.edge)
        d["fill"] = True
        d["zorder"] = 100
        return d

    def calc_path(self, GA):
        self.label_pos = ogdf.DPoint(
            (GA.x[self.edge.source()] + GA.x[self.edge.target()]) / 2,
            (GA.y[self.edge.source()] + GA.y[self.edge.target()]) / 2)
        src_arr = ogdf.DPolygon() if ogdf.python_matplotlib.isArrowEnabled(GA, self.edge.adjSource()) else nullptr
        tgt_arr = ogdf.DPolygon() if ogdf.python_matplotlib.isArrowEnabled(GA, self.edge.adjTarget()) else nullptr
        self.poly = ogdf.python_matplotlib.drawEdge(self.edge, GA, self.label_pos, src_arr, tgt_arr)
        self.bbox = ogdf.python_matplotlib.getBoundingBox(self.poly)
        self.src_arr.get_path().vertices = np.asarray(dPolylineToPathVertices(src_arr) if src_arr else [] + [(0, 0)], float)
        self.tgt_arr.get_path().vertices = np.asarray(dPolylineToPathVertices(tgt_arr) if tgt_arr else [] + [(0, 0)], float)
        return dPolylineToPath(self.poly)

    def _should_pick(self, artist, event):
        x, y = event.xdata, event.ydata
        if not x and x != 0:
            return False, None
        if not self.bbox.p1().m_x - self.PICK_DISTANCE <= x <= self.bbox.p2().m_x + self.PICK_DISTANCE:
            return False, None
        if not self.bbox.p1().m_y - self.PICK_DISTANCE <= y <= self.bbox.p2().m_y + self.PICK_DISTANCE:
            return False, None
        out = ogdf.DPoint()
        dist = ogdf.python_matplotlib.closestPointOnLine(self.poly, ogdf.DPoint(x, y), out)
        if dist <= self.PICK_DISTANCE:
            return True, {"point": out, "dist": dist}
        else:
            return False, None
