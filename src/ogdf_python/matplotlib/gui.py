import ipywidgets

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

        self.title = B("Selected Vertex")
        self.values = {
            "id": L("12"),
            "label": ipywidgets.Text("Label123"),
            "degree": L("3"),
            "position": L("123, 456"),
            "size": L("20 x 20"),
        }
        self.values["label"].continuous_update = True
        self.values["label"].on_submit(self.on_label_changed)

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
                grid_template_rows='80px auto auto', )
        )
        self.on_selection_changed()

    def on_label_changed(self, lbl):
        self.widget.GA.label[self.widget.selected.node] = lbl.value
        self.widget.selected.label.set_text(lbl.value)
        self.fig.canvas.draw_idle()

    def on_delete_clicked(self, btn):
        self.widget.GA.constGraph().delNode(self.widget.selected.node)

    def on_selection_changed(self):
        if self.widget.selected is None:
            self.pane.layout.visibility = 'hidden'
            return

        node = self.widget.selected.node
        GA = self.widget.GA
        self.pane.layout.visibility = 'visible'
        self.title.value = f"Selected Vertex {node.index()}"
        self.values["id"].value = f"{node.index()}"
        self.values["label"].value = str(GA.label[node])
        self.values["degree"].value = f"{node.degree()} ({node.indeg()} + {node.outdeg()})"
        self.values["position"].value = f"{GA.x[node]}, {GA.y[node]}"
        self.values["size"].value = f"{GA.width[node]} x {GA.height[node]}"
