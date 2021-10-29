import ipywidgets as widgets
from traitlets import Unicode, List, Dict
import cppyy


# See js/lib/ogdf-python-widget-view.js for the frontend counterpart to this file.

@widgets.register
class Widget(widgets.DOMWidget):
    # Name of the widget view class in front-end
    _view_name = Unicode('WidgetView').tag(sync=True)

    # Name of the widget model class in front-end
    _model_name = Unicode('WidgetModel').tag(sync=True)

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

    nodes = List(Dict().tag(sync=True)).tag(sync=True)
    links = List(Dict().tag(sync=True)).tag(sync=True)

    onclick_callback = None

    def __init__(self, graph_attributes):
        super().__init__()
        self.graph_attributes = graph_attributes
        self.on_msg(lambda *args: self.handle_msg(args[1]))
        self.export_graph()
        self.myObserver = MyGraphObserver(self.graph_attributes.constGraph(), self)

    def handle_msg(self, msg):
        if msg['code'] == 'linkClicked':
            self.onlick_callback(msg['code'], self.get_link_from_id(msg['id']), self.graph_attributes)
        elif msg['code'] == 'nodeClicked':
            self.onlick_callback(msg['code'], self.get_node_from_id(msg['id']), self.graph_attributes)
        elif msg['code'] == 'nodeMoved':
            self.move_node_to(self.get_node_from_id(msg['id']), msg['x'], msg['y'])
        elif msg['code'] == 'bendMoved':
            self.move_bend_to(self.get_link_from_id(msg['edgeId']), msg['x'], msg['y'], msg['bendIndex'])
        print(msg)

    def get_node_from_id(self, node_id):
        for node in self.graph_attributes.constGraph().nodes:
            if node.index() == int(node_id):
                return node

    def get_link_from_id(self, link_id):
        for link in self.graph_attributes.constGraph().edges:
            if link.index() == int(link_id):
                return link

    def move_node_to(self, node, x, y):
        self.graph_attributes.x[node] = x
        self.graph_attributes.y[node] = y

    def move_bend_to(self, edge, x, y, bend_nr):
        bend = None

        for i, point in enumerate(self.graph_attributes.bends(edge)):
            if i == bend_nr:
                bend = point
                break

        bend.m_x = x
        bend.m_y = y

    def refresh_graph(self):
        self.send({"code": "clearGraph"})
        self.export_graph()

    def enable_node_movement(self, enable):
        self.send({"code": "enableNodeMovement", "value": enable})

    def enable_bend_movement(self, enable):
        self.send({"code": "enableBendMovement", "value": enable})

    def color_to_dict(self, color):
        color = {"r": color.red(),
                 "g": color.green(),
                 "b": color.blue(),
                 "a": color.alpha()}
        return color

    def export_graph(self):
        nodes_data = []
        for node in self.graph_attributes.constGraph().nodes:
            node_dict = {"id": str(node.index()),
                         "name": str(self.graph_attributes.label(node)),
                         "x": int(self.graph_attributes.x(node) + 0.5),
                         "y": int(self.graph_attributes.y(node) + 0.5),
                         "shape": self.graph_attributes.shape(node),
                         "fillColor": self.color_to_dict(self.graph_attributes.fillColor(node)),
                         "strokeColor": self.color_to_dict(self.graph_attributes.strokeColor(node)),
                         "strokeWidth": self.graph_attributes.strokeWidth(node)}

            nodes_data.append(node_dict)

        links_data = []

        for edge in self.graph_attributes.constGraph().edges:
            bends = []
            for i, point in enumerate(self.graph_attributes.bends(edge)):
                bends.append([int(point.m_x + 0.5), int(point.m_y + 0.5)])

            links_data.append(
                {"id": str(edge.index()),
                 "s_id": str(edge.source().index()),
                 "t_id": str(edge.target().index()),
                 "t_shape": self.graph_attributes.shape(edge.target()),
                 "strokeColor": self.color_to_dict(self.graph_attributes.strokeColor(edge)),
                 "strokeWidth": self.graph_attributes.strokeWidth(edge),
                 "sx": int(self.graph_attributes.x(edge.source()) + 0.5),
                 "sy": int(self.graph_attributes.y(edge.source()) + 0.5),
                 "tx": int(self.graph_attributes.x(edge.target()) + 0.5),
                 "ty": int(self.graph_attributes.y(edge.target()) + 0.5),
                 "arrow": self.graph_attributes.arrowType(edge) == 1,
                 "bends": bends})

        self.set_trait('nodes', nodes_data)
        self.set_trait('links', links_data)


class MyGraphObserver(cppyy.gbl.ogdf.GraphObserver):
    def __init__(self, graph, widget):
        super().__init__(graph)
        self.widget = widget

    def nodeDeleted(self, node):
        self.widget.send({'code': 'deleteNodeById', 'data': str(node.index())})

    def nodeAdded(self, node):
        self.widget.send("nodeAdded")
        print("nodeAdded")

    def edgeDeleted(self, edge):
        self.widget.send({'code': 'deleteLinkById', 'data': str(edge.index())})

    def edgeAdded(self, edge):
        self.widget.send("edgeAdded")
        print("edgeAdded")

    def reInit(self):
        self.widget.send("reInit")
        print("reInit")

    def cleared(self):
        self.widget.send({'code': 'clearGraph'})
