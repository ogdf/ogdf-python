import ipywidgets

from ogdf_python.matplotlib.artist import NodeArtist
from ogdf_python.matplotlib.util import new_figure
from ogdf_python.matplotlib.widget import MatplotlibGraphEditor

L = ipywidgets.Label


def B(*args, **kwargs):
    l = L(*args, **kwargs)
    l.style.font_weight = "bold"
    return l


UI_STYLE = """
<style>
.ogdf_grapheditor_pane {
    background: white;
    z-index: 2;
    border-top-left-radius: 10px;
    border-top: 1px solid grey;
    border-left: 1px solid grey;
    padding-top: 10px;
    padding-left: 10px;
}
.ogdf_grapheditor_pane .widget-gridbox {
    overflow: visible;
}
</style>
""".strip()


class GraphEditorLayout(ipywidgets.GridBox):
    def __init__(self, GA):
        self.fig = new_figure()
        self.widget = MatplotlibGraphEditor(GA, self.fig.subplots())
        self.widget.on_selection_changed = self.on_selection_changed
        self.widget.on_node_moved = self.on_node_moved

        self.title = B("Selected Vertex")
        self.values = {
            "id": L("12"),
            "label": ipywidgets.Text("Label123", layout=ipywidgets.Layout(width="100px")),
            "degree": L("3"),
            "position": L("123, 456"),
            "width": ipywidgets.IntText("20", layout=ipywidgets.Layout(width="45px")),
            "height": ipywidgets.IntText("20", layout=ipywidgets.Layout(width="45px")),
        }
        self.values["size"] = ipywidgets.HBox([self.values["width"], self.values["height"]])
        self.values["width"].continuous_update = True
        self.values["width"].observe(self.on_size_changed, names='value')
        self.values["height"].continuous_update = True
        self.values["height"].observe(self.on_size_changed, names='value')
        self.values["label"].continuous_update = True
        self.values["label"].observe(self.on_label_changed, names='value')

        self.buttons = {
            "del": ipywidgets.Button(description="Delete", button_style="danger", icon="trash")
        }
        self.buttons["del"].on_click(self.on_delete_clicked)
        self.pane = ipywidgets.VBox([
            self.title,
            ipywidgets.GridBox(children=[
                B("ID"), self.values["id"],
                B("Label"), self.values["label"],
                B("Degree"), self.values["degree"],
                B("Position"), self.values["position"],
                B("Size"), self.values["size"],
            ], layout=ipywidgets.Layout(width="100%", grid_template_columns='1fr 2fr', padding="10px")),
            ipywidgets.HBox(list(self.buttons.values()))
        ])

        self.fig.canvas.layout.grid_area = "1/1/4/3"
        self.pane.layout.grid_area = "3/2/4/3"
        self.pane.add_class("ogdf_grapheditor_pane")

        # bar = ipywidgets.HBox([ipywidgets.Button(label="add")])
        # bar.layout.grid_area = "1/2/2/3"

        super().__init__(
            children=[self.fig.canvas, self.pane, ipywidgets.HTML(UI_STYLE)],
            layout=ipywidgets.Layout(
                width=f"{self.fig.get_figwidth() * 100}px", height=f"{self.fig.get_figheight() * 100}px",
                grid_template_columns='auto 200px',
                grid_template_rows='80px auto auto')
        )
        self.on_selection_changed()

    def on_node_moved(self, node):
        if not isinstance(self.widget.selected, NodeArtist) or self.widget.selected.node != node:
            return
        GA = self.widget.GA
        self.values["position"].value = f"{GA.x[node]:.1f}, {GA.y[node]:.1f}"

    def on_size_changed(self, x):
        self.widget.GA.width[self.widget.selected.node] = self.values["width"].value
        self.widget.GA.height[self.widget.selected.node] = self.values["height"].value
        self.widget.selected.update_attributes(self.widget.GA)
        self.fig.canvas.draw_idle()

    def on_label_changed(self, x):
        value = self.values["label"].value
        self.widget.GA.label[self.widget.selected.node] = value
        self.widget.selected.label.set_text(value)
        self.fig.canvas.draw_idle()

    def on_delete_clicked(self, btn):
        self.widget.GA.constGraph().delNode(self.widget.selected.node)

    def on_selection_changed(self):
        if isinstance(self.widget.selected, NodeArtist):
            node = self.widget.selected.node
            GA = self.widget.GA
            self.pane.layout.visibility = 'visible'
            self.title.value = f"Selected Vertex {node.index()}"
            self.values["id"].value = f"{node.index()}"
            self.values["label"].value = str(GA.label[node])
            self.values["degree"].value = f"{node.degree()} ({node.indeg()} + {node.outdeg()})"
            self.values["position"].value = f"{GA.x[node]:.1f}, {GA.y[node]:.1f}"
            self.values["width"].value = GA.width[node]
            self.values["height"].value = GA.height[node]
        else:
            self.pane.layout.visibility = 'hidden'
