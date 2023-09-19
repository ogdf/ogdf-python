from matplotlib import patheffects as patheffects
from matplotlib.backend_bases import MouseButton

from ogdf_python.loader import *
from ogdf_python.matplotlib.artist import NodeArtist, EdgeArtist
from ogdf_python.matplotlib.util import new_figure


class SimpleGraphObserver(ogdf.GraphObserver):
    def cleared(self):
        pass

    def nodeAdded(self, n):
        pass

    def edgeAdded(self, e):
        pass

    def nodeDeleted(self, node):
        pass

    def edgeDeleted(self, edge):
        pass

    def reInit(self):
        pass


class MatplotlibGraph:
    def __init__(self, GA, ax=None, apply_style=True, hide_spines=True):
        self.GA = GA
        if ax is None:
            self.ax = ax = new_figure().subplots()
        else:
            self.ax = ax
        G = GA.constGraph()
        self.nodes = {}  # TODO ogdf.NodeArray["PyObject*"](G, typed_nullptr("PyObject"))
        self.edges = {}
        # TODO clusters

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

        if apply_style:
            self.apply_style()
        if hide_spines:
            self.hide_spines()

        self._on_pick_cid = ax.figure.canvas.mpl_connect('pick_event', self._on_pick)
        self._on_click_cid = ax.figure.canvas.mpl_connect('button_press_event', self._on_click)
        self._on_close_cid = ax.figure.canvas.mpl_connect('close_event', self._on_close)
        self._last_pick_mouse_event = None

        # cppyy is somewhat picky when it comes to deriving from GraphObserver
        # so we try to keep this class as simple as possible
        self._graph_observer = SimpleGraphObserver(G)
        for m in ["cleared", "nodeDeleted", "edgeDeleted", "nodeAdded", "edgeAdded", "reInit"]:
            setattr(self._graph_observer, m, getattr(self, m))

    def cleared(self):
        for na in self.nodes.values():
            na.remove()
        for ea in self.edges.values():
            ea.remove()
        self.nodes.clear()
        self.edges.clear()
        self.ax.figure.canvas.draw_idle()

    def nodeDeleted(self, node):
        self.nodes[node].remove()
        del self.nodes[node]
        self.ax.figure.canvas.draw_idle()

    def edgeDeleted(self, edge):
        self.edges[edge].remove()
        del self.edges[edge]
        self.ax.figure.canvas.draw_idle()

    def nodeAdded(self, n):
        a = self.nodes[n] = NodeArtist(n, self.GA)
        self.ax.add_patch(a)
        self.ax.add_artist(a.label)
        self.ax.figure.canvas.draw_idle()

    def edgeAdded(self, e):
        cid = None

        # we need to defer drawing as not all attributes can already be accessed in the
        # edgeAdded callback
        def addedge(arg):
            nonlocal cid
            if cid is None:
                return
            self.ax.figure.canvas.mpl_disconnect(cid)
            cid = None
            a = self.edges[e] = EdgeArtist(e, self.GA)
            self.ax.add_patch(a)
            self.ax.add_artist(a.label)
            self.ax.add_patch(a.src_arr)
            self.ax.add_patch(a.tgt_arr)

        cid = self.ax.figure.canvas.mpl_connect('draw_event', addedge)
        self.ax.figure.canvas.draw_idle()

    def reInit(self):
        self.cleared()

    def _on_close(self, event):
        del self._graph_observer

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
        # fig.canvas.layout.min_height = '400px'
        # fig.canvas.layout.min_width = '100%'
        # fig.canvas.layout.width = '100%'

    def hide_spines(self):
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.figure.subplots_adjust(left=0, right=1, top=1, bottom=0)
        self.ax.figure.canvas.draw_idle()

    def update_all(self, GA):
        for na in self.nodes.values():
            na.update_attributes(GA)
        for ea in self.edges.values():
            ea.update_attributes(GA)
        self.ax.figure.canvas.draw_idle()

    def _ipython_display_(self):
        from IPython.core.display_functions import display
        return display(self.ax.figure.canvas)


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
        print("edge click")
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
