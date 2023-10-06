import functools
import traceback
from collections import defaultdict

from matplotlib import patheffects as patheffects
from matplotlib.axes import Axes
from matplotlib.backend_bases import MouseButton
from matplotlib.collections import *
from matplotlib.text import Text

from ogdf_python.loader import *
from ogdf_python.matplotlib.artist import NodeArtist, EdgeArtist
from ogdf_python.matplotlib.util import *


def catch_exception(wrapped):
    @functools.wraps(wrapped)
    def fun(*args, **kwargs):
        try:
            wrapped(*args, **kwargs)
        except Exception:
            traceback.print_exc()
            pass

    return fun


class BaseMatplotlibGraph:
    ax = None

    def __init__(self, apply_style=True, hide_spines=True):
        if apply_style:
            self.apply_style()
        if hide_spines:
            self.hide_spines()

        self._on_pick_cid = self.ax.figure.canvas.mpl_connect('pick_event', self._on_pick)
        self._on_click_cid = self.ax.figure.canvas.mpl_connect('button_press_event', self._on_click)
        self._last_pick_mouse_event = None

    def _on_pick(self, event):
        # me = event.mouseevent
        # print('%s click pick: artist=%s, button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #       ('double' if me.dblclick else 'single', event.artist, me.button,
        #        me.x, me.y, me.xdata, me.ydata))
        if event.mouseevent.button != MouseButton.LEFT:
            return
        elif self._last_pick_mouse_event == event.mouseevent:
            return  # ignore multiple picks from the same click
        elif isinstance(event.artist, NodeArtist):
            self.on_node_click(event.artist.node, event)
        elif isinstance(event.artist, EdgeArtist):
            self.on_edge_click(event.artist.edge, event)
        else:
            return
        self._last_pick_mouse_event = event.mouseevent
        return

    def _on_click(self, event):
        if self._last_pick_mouse_event == event:
            return  # ignore multiple click if it resulted in a pick
        # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #       ('double' if event.dblclick else 'single', event.button,
        #        event.x, event.y, event.xdata, event.ydata))
        self.on_background_click(event)

    def on_edge_click(self, edge, event):
        pass

    def on_node_click(self, node, event):
        pass

    def on_background_click(self, event):
        pass

    def apply_style(self):
        self.ax.set_aspect(1, anchor="C", adjustable="datalim")
        self.ax.autoscale()
        fig = self.ax.figure
        fig.canvas.header_visible = False
        fig.canvas.footer_visible = False
        fig.canvas.capture_scroll = True

        if fig.canvas.toolbar and hasattr(self, "update_all"):
            def update(*args, **kwargs):
                self.update_all()

            fig.canvas.toolbar.update_ogdf_graph = update
            fig.canvas.toolbar.toolitems = [*fig.canvas.toolbar.toolitems, ("Update", "Update the Graph", "refresh", "update_ogdf_graph")]
            fig.canvas.toolbar_visible = 'visible'

    def hide_spines(self):
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.ax.figure.canvas.draw_idle()

    def _ipython_display_(self):
        from IPython.core.display_functions import display
        return display(self.ax.figure.canvas)


class MatplotlibGraph(BaseMatplotlibGraph, ogdf.GraphObserver):
    def __init__(self, GA, ax=None, **kwargs):
        self.GA = GA
        if ax is None:
            ax = new_figure().subplots()
        self.ax: Axes = ax
        G = GA.constGraph()

        # TODO ogdf.NodeArray["PyObject*"](G, typed_nullptr("PyObject"))
        # TODO clusters
        self.nodes = {}
        self.edges = {}
        for n in G.nodes:
            a = self.nodes[n] = NodeArtist(n, GA)
            ax.add_patch(a)
            ax.add_artist(a.label)
        for e in G.edges:
            a = self.edges[e] = EdgeArtist(e, GA)
            ax.add_patch(a)
            ax.add_artist(a.label)
            # if len(a.src_arr.get_path().vertices) >= 2:
            ax.add_patch(a.src_arr)
            ax.add_patch(a.tgt_arr)

        BaseMatplotlibGraph.__init__(self, **kwargs)
        ogdf.GraphObserver.__init__(self, GA.constGraph())

    def __del__(self):
        ogdf.GraphObserver.__destruct__(self)

    @catch_exception
    def cleared(self):
        for na in self.nodes.values():
            na.remove()
        for ea in self.edges.values():
            ea.remove()
        self.nodes.clear()
        self.edges.clear()
        self.ax.figure.canvas.draw_idle()

    @catch_exception
    def nodeDeleted(self, node):
        if node not in self.nodes:
            return
        self.nodes[node].remove()
        del self.nodes[node]
        self.ax.figure.canvas.draw_idle()

    @catch_exception
    def edgeDeleted(self, edge):
        if edge not in self.edges:
            return
        self.edges[edge].remove()
        del self.edges[edge]
        self.ax.figure.canvas.draw_idle()

    @catch_exception
    def nodeAdded(self, node):
        a = self.nodes[node] = NodeArtist(node, self.GA)
        self.ax.add_patch(a)
        self.ax.add_artist(a.label)
        self.ax.figure.canvas.draw_idle()

    @catch_exception
    def edgeAdded(self, edge):
        cid = None
        index = edge.index()

        # we need to defer drawing as not all attributes can already be accessed in the
        # edgeAdded callback
        @catch_exception
        def addedge(arg):
            nonlocal cid
            if cid is None:
                return
            self.ax.figure.canvas.mpl_disconnect(cid)
            cid = None

            e = self.GA.constGraph().edges.byid(index)
            if e in self.edges:
                return
            a = self.edges[e] = EdgeArtist(e, self.GA)
            self.ax.add_patch(a)
            self.ax.add_artist(a.label)
            self.ax.add_patch(a.src_arr)
            self.ax.add_patch(a.tgt_arr)

        cid = self.ax.figure.canvas.mpl_connect('draw_event', addedge)
        self.ax.figure.canvas.draw_idle()

    @catch_exception
    def reInit(self):
        self.cleared()

    def update_all(self, GA=None):
        if GA is None:
            GA = self.GA
        else:
            self.GA = GA
        for na in self.nodes.values():
            na.update_attributes(GA)
        for ea in self.edges.values():
            ea.update_attributes(GA)
        self.ax.figure.canvas.draw_idle()


class HugeMatplotlibGraph(BaseMatplotlibGraph):
    EDGE_CLICK_WIDTH_PX = 10

    def __init__(self, GA, ax=None, add_node_labels=False, add_edge_labels=False, **kwargs):
        self.GA = GA
        if ax is None:
            ax = new_figure().subplots()
        self.ax: Axes = ax
        G = GA.constGraph()

        self.nodes_styles = defaultdict(list)
        for n in G.nodes:
            self.nodes_styles[NodeStyle.from_GA(GA, n)].append(n)
        for style, nodes in self.nodes_styles.items():
            # shape = get_node_shape(0, 0, style.width, style.height, style.shape)
            # offsets = [(GA.x[n], GA.y[n]) for n in nodes]
            paths = [get_node_shape(GA.x[n], GA.y[n], GA.width[n], GA.height[n], GA.shape[n]) for n in nodes]
            d = {k + 's': v for k, v in style.asdict().items() if v}  # and k not in {"shape", "width", "height"}
            ax.add_collection(PathCollection(
                paths=paths, zorder=200, **d))

        self.label_pos = ogdf.EdgeArray[ogdf.DPoint](G)
        self.edge_styles = defaultdict(list)
        for e in G.edges:
            self.edge_styles[EdgeStyle.from_GA(GA, e)].append(e)
        for style, edges in self.edge_styles.items():
            paths = [get_edge_path(GA, e, label_pos=self.label_pos[e], closed=True) for e in edges]
            d = {k + 's': v for k, v in style.asdict().items() if v}
            ax.add_collection(PathCollection(
                paths=paths, zorder=100, facecolors=d.get("edgecolors", None), **d))

        self.node_labels = {}
        self.auto_node_labels = add_node_labels
        if add_node_labels:
            for n in G.nodes:
                self.add_node_label(n)

        self.edge_labels = {}
        self.auto_edge_labels = add_edge_labels
        if add_edge_labels:
            for e in G.edges:
                self.add_edge_label(e)

        self._on_click_cid = self.ax.figure.canvas.mpl_connect('button_press_event', self._on_click)

        BaseMatplotlibGraph.__init__(self, **kwargs)
        # TODO updates
        # TODO highlight selected

    def _on_click(self, event):
        # print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #       ('double' if event.dblclick else 'single', event.button,
        #        event.x, event.y, event.xdata, event.ydata))
        if event.button != MouseButton.LEFT:
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
            # if self.point:
            #     self.point.remove()
            # self.point = self.ax.scatter([p.m_x], [p.m_y])
            self.on_edge_click(o, event)
        else:
            print(f"Clicked on a weird {type(o)} object {o!r}")

    def add_edge_label(self, e):
        GA = self.GA
        self.edge_labels[e] = t = Text(
            x=self.label_pos[e].m_x, y=self.label_pos[e].m_y,
            text=GA.label[e],
            color=color(GA.strokeColor[e]),
            verticalalignment='center', horizontalalignment='center',
            zorder=300,
        )
        self.ax.add_artist(t)

    def add_node_label(self, n):
        GA = self.GA
        self.node_labels[n] = t = Text(
            x=GA.x[n], y=GA.y[n],
            text=GA.label[n],
            color=color(GA.strokeColor[n]),
            verticalalignment='center', horizontalalignment='center',
            zorder=300,
        )
        self.ax.add_artist(t)


class MatplotlibGraphEditor(MatplotlibGraph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.selected = None
        self.dragging = False

        self.ax.figure.canvas.mpl_connect('key_press_event', self._on_key)
        self.ax.figure.canvas.mpl_connect('button_release_event', self._on_release)
        self.ax.figure.canvas.mpl_connect('motion_notify_event', self._on_motion)

    def nodeDeleted(self, node):
        if isinstance(self.selected, NodeArtist) and self.selected.node == node:
            self.unselect()
        super().nodeDeleted(node)

    def edgeDeleted(self, edge):
        if isinstance(self.selected, EdgeArtist) and self.selected.edge == edge:
            self.unselect()
        super().edgeDeleted(edge)

    def unselect(self, notify=True):
        if self.selected is None:
            return
        self.selected.set_path_effects([patheffects.Normal()])
        self.selected = None

        if notify:
            self.on_selection_changed()
        self.ax.figure.canvas.draw_idle()

    def select(self, artist):
        self.unselect(notify=False)
        self.selected = artist
        artist.set_path_effects([patheffects.withStroke(linewidth=5, foreground='blue')])

        self.on_selection_changed()
        self.ax.figure.canvas.draw_idle()

    def on_background_click(self, event):
        super().on_background_click(event)
        if event.dblclick:
            n = self.GA.constGraph().newNode()
            self.GA.label[n] = f"N{n.index()}"
            self.GA.x[n] = event.xdata
            self.GA.y[n] = event.ydata
            self.nodes[n].update_attributes(self.GA)
            self.select(self.nodes[n])
            return

    def on_selection_changed(self):
        pass

    def on_node_moved(self, node):
        pass

    def on_node_click(self, node, event):
        super().on_node_click(node, event)
        if isinstance(self.selected, NodeArtist) and self.selected != event.artist and \
                "ctrl" in event.mouseevent.modifiers:
            self.GA.constGraph().newEdge(self.selected.node, event.artist.node)
            return

        self.dragging = True
        self.select(event.artist)

    def on_edge_click(self, edge, event):
        super().on_edge_click(edge, event)
        self.dragging = False
        self.select(event.artist)

    def _on_key(self, event):
        if event.key == "delete":
            if isinstance(self.selected, NodeArtist):
                self.GA.constGraph().delNode(self.selected.node)
            elif isinstance(self.selected, EdgeArtist):
                self.GA.constGraph().delEdge(self.selected.edge)

    def _on_release(self, event):
        self.dragging = False

    def _on_motion(self, event):
        if not self.dragging or not isinstance(self.selected, NodeArtist):
            return
        node = self.selected.node
        self.GA.x[node] = event.xdata
        self.GA.y[node] = event.ydata
        self.selected.update_attributes(self.GA)
        for adj in node.adjEntries:
            self.edges[adj.theEdge()].update_attributes(self.GA)

        self.on_node_moved(node)
        self.ax.figure.canvas.draw_idle()
