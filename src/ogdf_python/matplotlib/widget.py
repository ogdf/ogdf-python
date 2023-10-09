import functools
import traceback
from typing import Dict, Tuple, List

import numpy as np
import sys
from itertools import chain
from matplotlib import patheffects
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseButton
from matplotlib.patches import PathPatch
from matplotlib.text import Text

from ogdf_python.loader import *
from ogdf_python.matplotlib.util import *


def catch_exception(wrapped):
    @functools.wraps(wrapped)
    def fun(*args, **kwargs):
        try:
            wrapped(*args, **kwargs)
        except Exception:
            # traceback.print_stack()
            traceback.print_exc()
            pass

    return fun


class MatplotlibGraph(ogdf.GraphObserver):
    EDGE_CLICK_WIDTH_PX = 10

    def __init__(self, GA, ax=None, add_nodes=True, add_edges=True,
                 auto_node_labels=None, auto_edge_labels=None, apply_style=True, hide_spines=True):
        super().__init__(GA.constGraph())
        self.GA = GA
        if ax is None:
            ax = new_figure().subplots()
        self.ax: Axes = ax
        G = GA.constGraph()

        if auto_node_labels is None:
            auto_node_labels = G.numberOfNodes() < 100
        if auto_edge_labels is None:
            auto_edge_labels = auto_node_labels
        self.node_labels: Dict[ogdf.node, Text] = dict()
        self.auto_node_labels: bool = auto_node_labels
        self.edge_labels: Dict[ogdf.edge, Text] = dict()
        self.auto_edge_labels: bool = auto_edge_labels

        # node -> (style, index)
        self.node_styles: Dict[ogdf.node, Tuple[NodeStyle, int]] = dict()
        # style -> (nodes, paths, collection, hatch_collection)
        self.style_nodes: Dict[NodeStyle, StyledElementCollection] = dict()

        # edge -> (style, index)
        self.edge_styles: Dict[ogdf.edge, Tuple[EdgeStyle, int]] = dict()
        # style -> (edges, paths, collection)
        self.style_edges: Dict[EdgeStyle, StyledElementCollection] = dict()

        self.label_pos = ogdf.EdgeArray[ogdf.DPoint](G)
        self.pending_additions: List[Tuple[str, int]] = []
        self.addition_timer = ax.figure.canvas.new_timer()
        self.addition_timer.add_callback(self.process_additions)
        self.addition_timer.interval = 100
        self.addition_timer.single_shot = True

        if add_nodes:
            for n in G.nodes:
                self.add_node(n)
        if add_edges:
            for e in G.edges:
                self.add_edge(e)
        if add_nodes or add_edges:
            for col in chain((s.coll for s in self.style_nodes.values()), (s.coll for s in self.style_edges.values())):
                self.ax.update_datalim(col.get_datalim(self.ax.transData).get_points())

        if apply_style:
            self.apply_style()
        if hide_spines:
            self.hide_spines()

        self._on_click_cid = self.ax.figure.canvas.mpl_connect('button_press_event', self._on_click)
        self.ax.figure.canvas.mpl_connect('close_event', lambda e: self.addition_timer.stop())

    def __del__(self):
        self.addition_timer.stop()
        self.__destruct__()

    def _on_click(self, event):
        # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #       ('double' if event.dblclick else 'single', event.button,
        #        event.x, event.y, event.xdata, event.ydata))
        if event.button != MouseButton.LEFT:
            return
        if self.ax.figure.canvas.toolbar.mode:  # PAN / ZOOM are truthy
            return
        t = self.ax.transData.inverted()
        a, _ = t.transform([0, 0])
        b, _ = t.transform([self.EDGE_CLICK_WIDTH_PX, self.EDGE_CLICK_WIDTH_PX])
        edge_width = abs(a - b)
        o, d, p = find_closest(self.GA, event.xdata, event.ydata, edge_width)
        # print(edge_width, o, d, p.m_x if p else 0, p.m_y if p else 0)
        if not o:
            # print("bg")
            self.on_background_click(event)
        elif isinstance(o, ogdf.NodeElement):
            # print("node", o)
            self.on_node_click(o, event)
        elif isinstance(o, ogdf.EdgeElement):
            # print("edge", o)
            # self.point = getattr(self, "point", None)
            # if self.point:
            #     self.point.remove()
            # self.point = self.ax.scatter([p.m_x], [p.m_y])
            self.on_edge_click(o, event)
        else:
            print(f"Clicked on a weird {type(o)} object {o!r}")

    def on_edge_click(self, edge, event):
        pass

    def on_node_click(self, node, event):
        pass

    def on_background_click(self, event):
        pass

    def update_all(self, autoscale=True):
        self.process_additions()
        for n in self.GA.constGraph().nodes:
            if n in self.node_styles:
                self.update_node(n)
        for e in self.GA.constGraph().edges:
            if e in self.edge_styles:
                self.update_edge(e)
        if autoscale:
            for col in chain((s.coll for s in self.style_nodes.values()), (s.coll for s in self.style_edges.values())):
                self.ax.update_datalim(col.get_datalim(self.ax.transData).get_points())
            self.ax.autoscale_view()
        self.ax.figure.canvas.draw_idle()

    def apply_style(self):
        self.ax.set_aspect(1, anchor="C", adjustable="datalim")
        self.ax.update_datalim([(0, 0), (100, 100)])
        self.ax.autoscale()
        self.ax.invert_yaxis()
        fig = self.ax.figure
        fig.canvas.header_visible = False
        fig.canvas.footer_visible = False
        fig.canvas.capture_scroll = False

        if fig.canvas.toolbar:
            def update(*args, **kwargs):
                self.update_all()

            fig.canvas.toolbar.update_ogdf_graph = update
            fig.canvas.toolbar.toolitems = [*fig.canvas.toolbar.toolitems,
                                            ("Update", "Update the Graph", "refresh", "update_ogdf_graph")]
            fig.canvas.toolbar_visible = 'visible'

    def hide_spines(self):
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.ax.figure.canvas.draw_idle()

    def _repr_mimebundle_(self, *args, **kwargs):
        from IPython.core.interactiveshell import InteractiveShell

        if not InteractiveShell.initialized():
            return {"text/plain": repr(self)}, {}

        fmt = InteractiveShell.instance().display_formatter
        display_en = fmt.ipython_display_formatter.enabled
        fmt.ipython_display_formatter.enabled = False
        try:
            data, meta = fmt.format(self.ax.figure.canvas, *args, **kwargs)
            # print("canvas", list(data.keys()) if data else "none")
            if list(data.keys()) != ["text/plain"] and data:
                return data, meta
            else:
                data, meta = fmt.format(self.ax.figure, *args, **kwargs)
                # print("figure", list(data.keys()) if data else "none")
                return data, meta
        finally:
            fmt.ipython_display_formatter.enabled = display_en

    #######################################################

    def process_additions(self):
        if not self.pending_additions:
            return
        pa, self.pending_additions = self.pending_additions, []

        for t, i in pa:
            if t == "node":
                cont, my_cont, fun = self.GA.constGraph().nodes, self.node_styles, self.add_node
            else:
                assert t == "edge"
                cont, my_cont, fun = self.GA.constGraph().edges, self.edge_styles, self.add_edge

            try:
                obj = cont.byid(i)
            except LookupError:
                continue

            if not obj or obj in my_cont:
                # no longer exists or already added
                continue

            try:
                fun(obj)
            except Exception as e:
                print(f"Could not add new {t} {i} ({obj}): {e}", sys.stderr)
                traceback.print_exc()

        self.ax.figure.canvas.draw_idle()

    @catch_exception
    def cleared(self):
        # for r in chain(self.node_labels.values(), self.edge_labels.values(),
        #                self.style_nodes.values(), self.style_edges.values()):
        #     r.remove()
        self.ax.clear()
        # sensible default
        self.ax.update_datalim([(0, 0), (100, 100)])
        self.ax.autoscale_view()
        self.node_labels.clear()
        self.edge_labels.clear()
        self.node_styles.clear()
        self.style_nodes.clear()
        self.edge_styles.clear()
        self.style_edges.clear()

    @catch_exception
    def nodeDeleted(self, node):
        if node not in self.node_styles:
            return
        self.remove_node(node)

    @catch_exception
    def edgeDeleted(self, edge):
        if edge not in self.edge_styles:
            return
        self.remove_edge(edge)

    @catch_exception
    def nodeAdded(self, node):
        self.pending_additions.append(("node", node.index()))
        self.addition_timer.start()

    @catch_exception
    def edgeAdded(self, edge):
        self.pending_additions.append(("edge", edge.index()))
        self.addition_timer.start()

    @catch_exception
    def reInit(self):
        self.cleared()

    #######################################################

    def add_node(self, n, label=None):
        GA = self.GA
        style = NodeStyle.from_GA(GA, n)
        if style not in self.style_nodes:
            paths = []
            coll = self.style_nodes[style] = StyledElementCollection(
                [], paths, style.create_collection(paths), style.create_hatch_collection(paths)
            )
            self.ax.add_collection(coll.coll)
            if coll.hatch_coll:
                self.ax.add_collection(coll.hatch_coll)
        else:
            coll = self.style_nodes[style]

        path = get_node_shape(GA.x[n], GA.y[n], GA.width[n], GA.height[n], GA.shape[n])
        idx = coll.add_elem(n, path)
        self.node_styles[n] = (style, idx)
        assert coll.elems[idx] == n

        if (label is None and self.auto_node_labels) or label:
            self.add_node_label(n)

    def add_node_label(self, n):
        GA = self.GA
        self.node_labels[n] = t = self.node_styles[n][0].create_text(
            GA.label[n], GA.x[n], GA.y[n])
        self.ax.add_artist(t)

    def remove_node(self, n):
        label = self.node_labels.pop(n, None)
        if label:
            label.remove()

        if n not in self.node_styles:
            return
        style, idx = self.node_styles.pop(n)
        coll = self.style_nodes[style]
        assert coll.elems[idx] == n
        chgd = coll.remove_elem(idx)
        if chgd:
            self.node_styles[chgd] = (style, idx)
            assert coll.elems[idx] == chgd
        elif not coll.paths:
            coll.remove()
            del self.style_nodes[style]

    def update_node(self, n):
        GA = self.GA
        new_style = NodeStyle.from_GA(GA, n)
        old_style, idx = self.node_styles[n]
        label = self.node_labels.get(n, None)
        if new_style == old_style:
            if label:
                label.set_text(GA.label[n])
            coll = self.style_nodes[new_style]
            assert coll.elems[idx] == n
            path = get_node_shape(GA.x[n], GA.y[n], GA.width[n], GA.height[n], GA.shape[n])
            if not np.array_equal(coll.paths[idx].vertices, path.vertices):
                coll.paths[idx] = path
                coll.set_stale()
                if label:
                    label.set_x(GA.x[n])
                    label.set_y(GA.y[n])
        else:
            self.remove_node(n)
            self.add_node(n, bool(label))

    #######################################################

    def add_edge(self, e, label=None):
        GA = self.GA
        style = EdgeStyle.from_GA(GA, e)
        if style not in self.style_edges:
            paths = []
            coll = self.style_edges[style] = StyledElementCollection(
                [], paths, style.create_collection(paths), None
            )
            self.ax.add_collection(coll.coll)
        else:
            coll = self.style_edges[style]

        path = get_edge_path(GA, e, self.label_pos[e], True)
        idx = coll.add_elem(e, path)
        self.edge_styles[e] = (style, idx)
        assert coll.elems[idx] == e

        if (label is None and self.auto_edge_labels) or label:
            self.add_edge_label(e)

    def add_edge_label(self, e):
        GA = self.GA
        self.edge_labels[e] = t = self.edge_styles[e][0].create_text(
            GA.label[e], self.label_pos[e].m_x, self.label_pos[e].m_y)
        self.ax.add_artist(t)

    def remove_edge(self, e):
        label = self.edge_labels.pop(e, None)
        if label:
            label.remove()

        if e not in self.edge_styles:
            return
        style, idx = self.edge_styles.pop(e)
        coll = self.style_edges[style]
        assert coll.elems[idx] == e
        chgd = coll.remove_elem(idx)
        if chgd:
            self.edge_styles[chgd] = (style, idx)
            assert coll.elems[idx] == chgd
        elif not coll.paths:
            coll.remove()
            del self.style_edges[style]

    def update_edge(self, e):
        GA = self.GA
        new_style = EdgeStyle.from_GA(GA, e)
        old_style, idx = self.edge_styles[e]
        label = self.edge_labels.get(e, None)
        if new_style == old_style:
            if label:
                label.set_text(GA.label[e])
            coll = self.style_edges[new_style]
            assert coll.elems[idx] == e
            path = get_edge_path(GA, e, self.label_pos[e], True)
            if not np.array_equal(coll.paths[idx].vertices, path.vertices):
                coll.paths[idx] = path
                coll.set_stale()
                if label:
                    label.set_x(self.label_pos[e].m_x)
                    label.set_y(self.label_pos[e].m_y)
        else:
            self.remove_edge(e)
            self.add_edge(e, bool(label))


class MatplotlibGraphEditor(MatplotlibGraph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.selected = None
        self.selected_artist = None
        self.dragging = False

        self.ax.figure.canvas.mpl_connect('key_press_event', self._on_key)
        self.ax.figure.canvas.mpl_connect('button_release_event', self._on_release)
        self.ax.figure.canvas.mpl_connect('motion_notify_event', self._on_motion)

    def nodeDeleted(self, node):
        if self.selected == node:
            self.unselect()
        super().nodeDeleted(node)

    def edgeDeleted(self, edge):
        if self.selected == edge:
            self.unselect()
        super().edgeDeleted(edge)

    def unselect(self, notify=True):
        if self.selected is None:
            return
        self.selected = None
        if self.selected_artist is not None:
            self.selected_artist.remove()
            self.selected_artist = None

        if notify:
            self.on_selection_changed()
        self.ax.figure.canvas.draw_idle()

    def select(self, elem):
        self.unselect(notify=False)
        self.selected = elem
        if isinstance(elem, ogdf.NodeElement):
            style, idx = self.node_styles[elem]
            path = self.style_nodes[style].paths[idx]
        else:
            assert isinstance(elem, ogdf.EdgeElement)
            style, idx = self.edge_styles[elem]
            path = self.style_edges[style].paths[idx]
        self.selected_artist = PathPatch(
            path, fill=False,
            edgecolor=style.edgecolor, linestyle=style.linestyle, linewidth=style.linewidth,
            path_effects=[patheffects.withStroke(linewidth=5, foreground='blue')])
        self.ax.add_artist(self.selected_artist)

        self.on_selection_changed()
        self.ax.figure.canvas.draw_idle()

    def on_background_click(self, event):
        super().on_background_click(event)
        self.dragging = False
        if event.dblclick:
            n = self.GA.constGraph().newNode()
            self.GA.label[n] = f"N{n.index()}"
            self.GA.x[n] = event.xdata
            self.GA.y[n] = event.ydata
            self.update_node(n)
            self.select(n)
        elif "ctrl" not in event.modifiers:
            self.unselect()

    def on_selection_changed(self):
        pass

    def on_node_moved(self, node):
        pass

    def on_node_click(self, node, event):
        super().on_node_click(node, event)
        if isinstance(self.selected, ogdf.NodeElement) and self.selected != node and \
                "ctrl" in event.modifiers:
            self.GA.constGraph().newEdge(self.selected, node)
            return

        self.dragging = True
        self.select(node)

    def on_edge_click(self, edge, event):
        super().on_edge_click(edge, event)
        self.dragging = False
        self.select(edge)

    def _on_key(self, event):
        if event.key == "delete":
            if isinstance(self.selected, ogdf.NodeElement):
                self.GA.constGraph().delNode(self.selected)
            elif isinstance(self.selected, ogdf.EdgeElement):
                self.GA.constGraph().delEdge(self.selected)

    def _on_release(self, event):
        self.dragging = False

    def _on_motion(self, event):
        if not self.dragging or not self.selected or not isinstance(self.selected, ogdf.NodeElement):
            return
        node = self.selected
        self.GA.x[node] = event.xdata
        self.GA.y[node] = event.ydata
        self.update_node(node)
        for adj in node.adjEntries:
            self.update_edge(adj.theEdge())

        style, idx = self.node_styles[node]
        path = self.style_nodes[style].paths[idx]
        self.selected_artist.set_path(path)

        self.on_node_moved(node)
        self.ax.figure.canvas.draw_idle()
