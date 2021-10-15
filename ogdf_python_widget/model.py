import ipywidgets as widgets
from traitlets import Unicode, List, Dict


# See js/lib/ogdf-python-widget-view.js for the frontend counterpart to this file.

@widgets.register
class HelloWorld(widgets.DOMWidget):
    """An example widget."""

    # Name of the widget view class in front-end
    _view_name = Unicode('HelloView').tag(sync=True)

    # Name of the widget model class in front-end
    _model_name = Unicode('HelloModel').tag(sync=True)

    # Name of the front-end module containing widget view
    _view_module = Unicode('ogdf-python-widget').tag(sync=True)

    # Name of the front-end module containing widget model
    _model_module = Unicode('ogdf-python-widget').tag(sync=True)

    # Version of the front-end module containing widget view
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    # Version of the front-end module containing widget model
    _model_module_version = Unicode('^0.1.0').tag(sync=True)

    # Widget specific property.
    # Widget properties are defined as traitlets. Any property tagged with `sync=True`
    # is automatically synced to the frontend *any* time it changes in Python.
    # It is synced back to Python from the frontend *any* time the model is touched.
    # value = Unicode('Hello Test!').tag(sync=True)

    nodes = List(Dict()).tag(sync=True)
    links = List(Dict()).tag(sync=True)

    def __init__(self, graph_attributes):
        self.graph_attributes = graph_attributes
        self.on_msg(lambda *args: print(args[1]))
        self.export_graph()
        super().__init__()

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

        self.set_trait('nodes', nodes_data)
        self.set_trait('links', links_data)
        # self.send("init")