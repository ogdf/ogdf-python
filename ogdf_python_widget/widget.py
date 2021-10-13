import json

from ipywidgets import VBox, Button
from .example import HelloWorld
from ipykernel.comm import Comm


class GraphWidget(VBox):
    def __init__(self, graph_attributes):
        self.graph_attributes = graph_attributes
        self.drawing_pad = HelloWorld()
        self.c = Comm(target_name='myTarget', data={})
        load_button = Button(description="Load Graph", tooltip="Click me")
        load_button.on_click(lambda b: self.load_graph())
        self.export_graph()

        buttons = VBox([self.drawing_pad, load_button])
        super().__init__([buttons])

    def load_graph(self):
        self.c.send('C00')
        self.export_graph()

    def export_graph(self):
        nodes_data = []
        for node in self.graph_attributes.constGraph().nodes:
            nodes_data.append(
                {"id": str(node.index()), "name": str(node.index()), "x": int(self.graph_attributes.x(node) + 0.5),
                 "y": int(self.graph_attributes.y(node) + 0.5)})

        links_data = []

        for edge in self.graph_attributes.constGraph().edges:
            edge_id = str(edge.source().index()) + "_" + str(edge.target().index())
            prev_x = int(self.graph_attributes.x(edge.source()) + 0.5)
            prev_y = int(self.graph_attributes.y(edge.source()) + 0.5)

            for point in self.graph_attributes.bends(edge):
                links_data.append(
                    {"id": edge_id, "sx": prev_x, "sy": prev_y, "tx": int(point.m_x + 0.5), "ty": int(point.m_y + 0.5)})
                prev_x = int(point.m_x + 0.5)
                prev_y = int(point.m_y + 0.5)

            link_dict = {"id": edge_id, "sx": prev_x, "sy": prev_y,
                         "tx": int(self.graph_attributes.x(edge.target()) + 0.5),
                         "ty": int(self.graph_attributes.y(edge.target()) + 0.5)}
            if self.graph_attributes.arrowType(edge) == 1:
                link_dict['arrow'] = True
            links_data.append(link_dict)

        self.c.send('N00' + json.dumps(nodes_data))
        self.c.send('L00' + json.dumps(links_data))
