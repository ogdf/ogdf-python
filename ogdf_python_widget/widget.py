import cppyy
import ipywidgets as widgets
from traitlets import Unicode, Dict, Integer, Float, Bool
from datetime import datetime


# See js/lib/ogdf-python-widget-view.js for the frontend counterpart to this file.

def color_to_dict(color):
    color = {"r": color.red(),
             "g": color.green(),
             "b": color.blue(),
             "a": color.alpha()}
    return color


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

    width = Integer(960).tag(sync=True)
    height = Integer(540).tag(sync=True)
    x_pos = Float(0).tag(sync=True)
    y_pos = Float(0).tag(sync=True)
    zoom = Float(1).tag(sync=True)

    click_thickness = Integer(10).tag(sync=True)
    grid_size = Integer(0).tag(sync=True)
    animation_duration = Integer(1000).tag(sync=True)

    force_config = Dict().tag(sync=True)

    rescale_on_resize = Bool(True).tag(sync=True)
    node_movement_enabled = Bool(False).tag(sync=True)


    on_node_click_callback = None
    on_link_click_callback = None
    on_svg_click_callback = None
    on_node_moved_callback = None
    on_bend_moved_callback = None
    on_bend_clicked_callback = None

    def __init__(self, graph_attributes, debug=False):
        super().__init__()
        self.graph_attributes = graph_attributes
        self.on_msg(self.handle_msg)
        self.myObserver = MyGraphObserver(self.graph_attributes.constGraph(), self)
        self.debug = debug

    def set_graph_attributes(self, graph_attributes):
        self.graph_attributes = graph_attributes
        self.export_graph()
        self.myObserver = MyGraphObserver(self.graph_attributes.constGraph(), self)
        self.stop_force_directed()

    def update_graph_attributes(self, graph_attributes):
        if self.graph_attributes.constGraph() is graph_attributes.constGraph():
            if self.force_config != {} and not self.force_config['stop']:
                self.stop_force_directed()
            self.graph_attributes = graph_attributes
            self.update_all_nodes()
            self.update_all_links()
        else:
            print("Your GraphAttributes need to depend on the same Graph in order to work. \nTo completely update the "
                  "GraphAttributes use set_graph_attributes(GA)")

    def handle_msg(self, *args):
        msg = args[1]
        if msg['code'] == 'linkClicked':
            if self.on_link_click_callback is not None:
                self.on_link_click_callback(self.get_link_from_id(msg['id']), msg['altKey'], msg['ctrlKey'])
        elif msg['code'] == 'nodeClicked':
            if self.on_node_click_callback is not None:
                self.on_node_click_callback(self.get_node_from_id(msg['id']), msg['altKey'], msg['ctrlKey'])
        elif msg['code'] == 'nodeMoved':
            node = self.get_node_from_id(msg['id'])
            self.move_node_to(node, msg['x'], msg['y'])
            if self.on_node_moved_callback is not None:
                self.on_node_moved_callback(node, msg['x'], msg['y'])
        elif msg['code'] == 'bendMoved':
            link = self.get_link_from_id(msg['linkId'])
            self.move_bend_to(link, msg['x'], msg['y'], msg['bendIndex'])
            if self.on_bend_moved_callback is not None:
                self.on_bend_moved_callback(link, msg['x'], msg['y'], msg['bendIndex'])
        elif msg['code'] == 'bendClicked':
            link = self.get_link_from_id(msg['linkId'])
            if self.on_bend_clicked_callback is not None:
                self.on_bend_clicked_callback(link, msg['bendIndex'], msg['altKey'])
        elif msg['code'] == 'svgClicked':
            if self.on_svg_click_callback is not None:
                self.on_svg_click_callback(msg['x'], msg['y'], msg['altKey'], msg['ctrlKey'], msg['backgroundClicked'])
        elif msg['code'] == 'widgetReady':
            self.export_graph()
        elif msg['code'] == 'positionUpdate':
            self.position_update(msg['nodes'])
        if self.debug and msg['code'] != 'positionUpdate':
            print(msg)

    def position_update(self, nodes):
        if self.force_config == {} or self.force_config['stop']:
            return
        for node in nodes:
            n = self.get_node_from_id(node['id'])
            self.move_node_to(n, node['x'], node['y'])

    def start_force_directed(self, charge_force=-100, force_center_x=None, force_center_y=None, fix_start_position=True):
        for link in self.graph_attributes.constGraph().edges:
            self.graph_attributes.bends(link).clear()

        if force_center_x is None or force_center_y is None:
            center_coords = self.svgcoords_to_graphcoords(self.width / 2, self.height / 2)
            force_center_x = center_coords['x']
            force_center_y = center_coords['y']

        self.force_config = {"chargeForce": charge_force,
                             "forceCenterX": force_center_x,
                             "forceCenterY": force_center_y,
                             "fixStartPosition": fix_start_position,
                             "stop": False}

    def stop_force_directed(self):
        self.force_config = {"stop": True}
        self.refresh_graph()

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

    def move_link(self, link):
        self.send({"code": "moveLink", "data": self.link_to_dict(link)})

    def remove_all_bend_movers(self):
        self.send({"code": "removeAllBendMovers"})

    def remove_bend_mover_for_id(self, link_id):
        self.send({"code": "removeBendMoversFor", "data": str(link_id)})

    def update_node(self, node, animated=True):
        self.send({"code": "updateNode", "data": self.node_to_dict(node), "animated": animated})

    def update_link(self, link, animated=True):
        self.send({"code": "updateLink", "data": self.link_to_dict(link), "animated": animated})

    def update_all_nodes(self, animated=True):
        for node in self.graph_attributes.constGraph().nodes:
            self.update_node(node, animated)

    def update_all_links(self, animated=True):
        for link in self.graph_attributes.constGraph().edges:
            self.update_link(link, animated)

    def download_svg(self, file_name=None):
        if file_name is None:
            now = datetime.now()
            file_name = now.strftime("%d/%m/%Y %H:%M:%S")

        self.send({"code": "downloadSvg", "fileName": file_name})

    def svgcoords_to_graphcoords(self, svg_x, svg_y):
        g_x = svg_x / self.zoom - self.x_pos / self.zoom
        g_y = svg_y / self.zoom - self.y_pos / self.zoom
        return {'x': g_x, 'y': g_y}

    def node_to_dict(self, node):
        return {"id": str(node.index()),
                "name": str(self.graph_attributes.label(node)),
                "x": int(self.graph_attributes.x(node) + 0.5),
                "y": int(self.graph_attributes.y(node) + 0.5),
                "shape": self.graph_attributes.shape(node),
                "fillColor": color_to_dict(self.graph_attributes.fillColor(node)),
                "strokeColor": color_to_dict(self.graph_attributes.strokeColor(node)),
                "strokeWidth": self.graph_attributes.strokeWidth(node),
                "nodeWidth": self.graph_attributes.width(node),
                "nodeHeight": self.graph_attributes.height(node)}

    def link_to_dict(self, link):
        bends = []
        for i, point in enumerate(self.graph_attributes.bends(link)):
            bends.append([int(point.m_x + 0.5), int(point.m_y + 0.5)])

        link_dict = {"id": str(link.index()),
                     "label": str(self.graph_attributes.label(link)),
                     "source": str(link.source().index()),
                     "target": str(link.target().index()),
                     "t_shape": self.graph_attributes.shape(link.target()),
                     "strokeColor": color_to_dict(self.graph_attributes.strokeColor(link)),
                     "strokeWidth": self.graph_attributes.strokeWidth(link),
                     "sx": int(self.graph_attributes.x(link.source()) + 0.5),
                     "sy": int(self.graph_attributes.y(link.source()) + 0.5),
                     "tx": int(self.graph_attributes.x(link.target()) + 0.5),
                     "ty": int(self.graph_attributes.y(link.target()) + 0.5),
                     "arrow": self.graph_attributes.arrowType(link) == 1,
                     "bends": bends}

        if len(bends) > 0:
            link_dict["label_x"] = bends[0][0]
            link_dict["label_y"] = bends[0][1]
        else:
            link_dict["label_x"] = (link_dict["sx"] + link_dict["tx"]) / 2
            link_dict["label_y"] = (link_dict["sy"] + link_dict["ty"]) / 2

        return link_dict

    def export_graph(self):
        nodes_data = []
        for node in self.graph_attributes.constGraph().nodes:
            nodes_data.append(self.node_to_dict(node))

        links_data = []
        for link in self.graph_attributes.constGraph().edges:
            links_data.append(self.link_to_dict(link))

        self.send({'code': 'initGraph', 'nodes': nodes_data, 'links': links_data})


class MyGraphObserver(cppyy.gbl.ogdf.GraphObserver):
    def __init__(self, graph, widget):
        super().__init__(graph)
        self.widget = widget

    def nodeDeleted(self, node):
        self.widget.send({'code': 'deleteNodeById', 'data': str(node.index())})

    def nodeAdded(self, node):
        self.widget.send({'code': 'nodeAdded', 'data': self.widget.node_to_dict(node)})

    def edgeDeleted(self, edge):
        self.widget.send({'code': 'deleteLinkById', 'data': str(edge.index())})

    def edgeAdded(self, edge):
        self.widget.send({'code': 'linkAdded', 'data': self.widget.link_to_dict(edge)})

    def reInit(self):
        self.widget.export_graph()

    def cleared(self):
        self.widget.send({'code': 'clearGraph'})
