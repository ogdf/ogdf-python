from matplotlib import patheffects as patheffects

from ogdf_python.loader import *
from ogdf_python.matplotlib.artist import NodeArtist, EdgeArtist


class MatplotlibGraph(ogdf.GraphObserver):
    def __init__(self, GA, ax=None, apply_style=True, hide_spines=True):
        super().__init__(GA.constGraph())
        self.GA = GA
        if ax is None:
            import matplotlib.pyplot as plt
            self.ax = ax = plt.gca()
        else:
            self.ax = ax
        G = GA.constGraph()
        self.nodes = {}  # TODO ogdf.NodeArray["PyObject*"](G, typed_nullptr("PyObject"))
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

        if apply_style:
            self.apply_style()
        if hide_spines:
            self.hide_spines()

        self._on_pick_cid = ax.figure.canvas.mpl_connect('pick_event', self._on_pick)
        self._last_pick_mouse_event = None

    def cleared(self):
        for na in self.nodes.values():
            na.remove()
        for ea in self.edge.values():
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

    def edgeAdded(self, e):
        a = self.edges[e] = EdgeArtist(e, self.GA)
        self.ax.add_patch(a)
        self.ax.add_artist(a.label)
        self.ax.add_patch(a.src_arr)
        self.ax.add_patch(a.tgt_arr)

    def reInit(self):
        pass

    def _on_pick(self, event):
        if self._last_pick_mouse_event == event.mouseevent:
            return  # ignore multiple picks from the same click
        if isinstance(event.artist, NodeArtist):
            self.on_node_click(event.artist.node, event)
        elif isinstance(event.artist, EdgeArtist):
            self.on_edge_click(event.artist.edge, event)
        else:
            return
        self._last_pick_mouse_event = event.mouseevent
        return

    def on_edge_click(self, edge, event):
        pass

    def on_node_click(self, node, event):
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


class MatplotlibGraphEditor(MatplotlibGraph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.selected = None
        self.dragging = False

        self.ax.figure.canvas.mpl_connect('button_release_event', self._on_release)
        self.ax.figure.canvas.mpl_connect('motion_notify_event', self._on_motion)

    def nodeDeleted(self, node):
        if isinstance(self.selected, NodeArtist) and self.selected.node == node:
            self.unselect()
        super().nodeDeleted(node)

    def edgeDeleted(self, edge):
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

    def on_selection_changed(self):
        pass

    def on_node_click(self, node, event):
        super().on_node_click(node, event)
        self.dragging = True
        self.select(event.artist)

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

        self.ax.figure.canvas.draw_idle()
