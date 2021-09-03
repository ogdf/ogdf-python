from ipywidgets import HBox, VBox, Button
from .example import HelloWorld


class GraphWidget(VBox):
    def __init__(self, graph_attributes):
        self.graph_attributes = graph_attributes
        drawing_pad = HelloWorld()
        self.drawing_pad = drawing_pad
        add_button = Button(description="Add", tooltip="Click me")
        clear_button = Button(description="Clear", tooltip="Click me")
        refresh_button = Button(description="Refresh", tooltip="Click me")
        load_button = Button(description="Load Graph", tooltip="Click me")
        add_button.on_click(lambda b: self.test())
        clear_button.on_click(lambda b: self.clear())
        refresh_button.on_click(lambda b: self.refresh())
        load_button.on_click(lambda b: self.export_graph())
        self.count = 0
        self.test()
        self.export_graph()

        buttons = VBox([add_button, clear_button, refresh_button, load_button])
        super().__init__([buttons])

    def export_graph(self):
        nodes = []
        edges = []

        for node in self.graph_attributes.constGraph().nodes:
            x_coord = int(self.graph_attributes.x(node) + 0.5)
            y_coord = int(self.graph_attributes.y(node) + 0.5)
            nodes.append([x_coord, y_coord, str(node.index())])

        for edge in self.graph_attributes.constGraph().edges:
            prev_x = int(self.graph_attributes.x(edge.source()) + 0.5)
            prev_y = int(self.graph_attributes.y(edge.source()) + 0.5)

            for point in self.graph_attributes.bends(edge):
                edges.append([prev_x, prev_y, int(point.m_x + 0.5), int(point.m_y + 0.5)])
                prev_x = int(point.m_x + 0.5)
                prev_y = int(point.m_y + 0.5)

            edges.append([prev_x, prev_y, int(self.graph_attributes.x(edge.target()) + 0.5),
                          int(self.graph_attributes.y(edge.target()) + 0.5)])

        self.drawing_pad.set_trait('nodes', nodes)
        self.drawing_pad.set_trait('edges', edges)

    def test(self):
        self.count += 1
        self.drawing_pad.value = self.count.__str__()

    def clear(self):
        self.count = 0
        self.drawing_pad.value = self.count.__str__()

    def refresh(self):
        self.drawing_pad.refresh = not self.drawing_pad.refresh
