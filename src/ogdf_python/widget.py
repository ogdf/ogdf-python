from ipywidgets import HBox, VBox, Button
from .example import HelloWorld


class CustomBox(VBox):
    def __init__(self, graph_attributes):
        self.graph_attributes = graph_attributes
        drawing_pad = HelloWorld()
        button = Button(description="Add", tooltip="Click me")
        clear_button = Button(description="Clear", tooltip="Click me")
        button.on_click(lambda b: self.test())
        clear_button.on_click(lambda b: self.clear())
        self.drawing_pad = drawing_pad
        self.count = 0
        self.test()

        for node in graph_attributes.constGraph().nodes:
            drawing_pad.nodes.append([int(graph_attributes.x(node) + 0.5), int(graph_attributes.y(node) + 0.5),
                                     str(node.index())])

        for edge in graph_attributes.constGraph().edges:
            prev_x = int(graph_attributes.x(edge.source()) + 0.5)
            prev_y = int(graph_attributes.y(edge.source()) + 0.5)

            for point in graph_attributes.bends(edge):
                drawing_pad.edges.append([prev_x, prev_y, int(point.m_x + 0.5), int(point.m_y + 0.5)])
                prev_x = int(point.m_x + 0.5)
                prev_y = int(point.m_y + 0.5)

            drawing_pad.edges.append([prev_x, prev_y, int(graph_attributes.x(edge.target()) + 0.5),
                                      int(graph_attributes.y(edge.target()) + 0.5)])

        buttons = VBox([button, clear_button])
        super().__init__([buttons])

    def test(self):
        self.count += 1
        self.drawing_pad.value = self.count.__str__()

    def clear(self):
        self.count = 0
        self.drawing_pad.value = self.count.__str__()
