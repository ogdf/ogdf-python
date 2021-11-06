var widgets = require('@jupyter-widgets/base');
var _ = require('lodash');
var d3 = require("d3");
require("./style.css");

// See widget.py for the kernel counterpart to this file.


// Custom Model. Custom widgets models must at least provide default values
// for model attributes, including
//
//  - `_view_name`
//  - `_view_module`
//  - `_view_module_version`
//
//  - `_model_name`
//  - `_model_module`
//  - `_model_module_version`
//
//  when different from the base class.

// When serializing the entire widget state for embedding, only values that
// differ from the defaults will be specified.
var WidgetModel = widgets.DOMWidgetModel.extend({
    defaults: _.extend(widgets.DOMWidgetModel.prototype.defaults(), {
        _model_name: 'WidgetModel',
        _view_name: 'WidgetView',
        _model_module: 'ogdf-python-widget',
        _view_module: 'ogdf-python-widget',
        _model_module_version: '0.1.0',
        _view_module_version: '0.1.0',
        value: 'Hello Test!',
        width: 960,
        height: 540,
        x_pos: 0,
        y_pos: 0,
        zoom: 1,
    })
});

// Custom View. Renders the widget model.
var WidgetView = widgets.DOMWidgetView.extend({
    initialize: function (parameters) {
        WidgetView.__super__.initialize.call(this, parameters);

        this.isBendMovementEnabled = false
        this.isNodeMovementEnabled = false
        this.rescaleOnResize = true

        //only for internal use
        this.isRenderCallbackAllowed = true
        this.isTransformCallbackAllowed = true

        this.nodes = []
        this.links = []

        this.width = this.model.get('width')
        this.height = this.model.get('height')

        this.model.on('msg:custom', this.handle_msg.bind(this));

        this.model.on('change:links', this.renderCallbackCheck, this);
        this.model.on('change:nodes', this.renderCallbackCheck, this);

        this.model.on('change:x_pos', this.transformCallbackCheck, this);
        this.model.on('change:y_pos', this.transformCallbackCheck, this);
        this.model.on('change:zoom', this.transformCallbackCheck, this);

        this.model.on('change:width', this.svgSizeChanged, this)
        this.model.on('change:height', this.svgSizeChanged, this)
    },

    svgSizeChanged: function () {
        this.width = this.model.get('width')
        this.height = this.model.get('height')

        d3.select(this.svg)
            .attr("width", this.model.get('width'))
            .attr("height", this.model.get('height'))

        if (this.rescaleOnResize) this.readjustZoomLevel(15)
    },

    getInitialTransform: function (radius) {
        let boundingBox = this.getBoundingBox(this.nodes, this.links)

        const boundingBoxWidth = boundingBox.maxX - boundingBox.minX + radius * 2
        const boundingBoxHeight = boundingBox.maxY - boundingBox.minY + radius * 2

        let scale = Math.min(this.width / boundingBoxWidth, this.height / boundingBoxHeight);
        let x = this.width / 2 - (boundingBox.minX + boundingBoxWidth / 2 - radius) * scale;
        let y = this.height / 2 - (boundingBox.minY + boundingBoxHeight / 2 - radius) * scale;

        if (this.nodes.length === 1) {
            scale = 1
            x = this.width / 2 - this.nodes[0].x
            y = this.height / 2 - this.nodes[0].y
        }

        return d3.zoomIdentity.translate(x, y).scale(scale)
    },

    readjustZoomLevel: function (transform) {
        const widgetView = this
        const svg = d3.select(this.svg)

        //add zoom capabilities
        const zoom = d3.zoom();

        svg.call(zoom.transform, transform)
        svg.call(zoom.on('zoom', zoomed).on('end', zoomended));
        svg.call(zoom)
        this.g.attr("transform", transform)
        this.updateZoomLevelInModel(transform)

        function zoomed({transform}) {
            widgetView.g.attr("transform", transform);
        }

        function zoomended({transform}) {
            widgetView.updateZoomLevelInModel(transform)
        }
    },

    updateZoomLevelInModel: function (transform) {
        this.isTransformCallbackAllowed = false
        this.model.set("x_pos", transform.x)
        this.model.set("y_pos", transform.y)
        this.model.set("zoom", transform.k)
        this.model.save_changes()
        this.isTransformCallbackAllowed = true
    },

    transformCallbackCheck: function () {
        if (this.isTransformCallbackAllowed) {
            this.readjustZoomLevel(
                d3.zoomIdentity.translate(this.model.get('x_pos'), this.model.get('y_pos')).scale(this.model.get('zoom')))
            console.log("readjusting zoom")
        }
    },

    renderCallbackCheck: function () {
        if (this.isRenderCallbackAllowed) this.render()
    },

    handle_msg: function (msg) {
        if (msg.code === 'deleteNodeById') {
            this.isRenderCallbackAllowed = false
            this.deleteNodeById(msg.data)
            this.isRenderCallbackAllowed = true
        } else if (msg.code === 'deleteLinkById') {
            this.isRenderCallbackAllowed = false
            this.deleteLinkById(msg.data)
            this.isRenderCallbackAllowed = true
        } else if (msg.code === 'clearGraph') {
            this.isRenderCallbackAllowed = false
            this.clearGraph()
            this.isRenderCallbackAllowed = true
        } else if (msg.code === 'enableNodeMovement') {
            this.isNodeMovementEnabled = msg.value

            if (!this.isNodeMovementEnabled) {
                d3.select(this.svg).selectAll(".node").on('mousedown.drag', null);
                d3.select(this.svg).selectAll("text").on('mousedown.drag', null);
            } else {
                d3.select(this.svg).selectAll(".node").call(this.drag_handler)
                d3.select(this.svg).selectAll("text").call(this.drag_handler)
            }
        } else if (msg.code === 'enableBendMovement') {
            this.isBendMovementEnabled = msg.value

            if (!this.isBendMovementEnabled) {
                this.removeBendMovers()
            }
        } else if (msg.code === 'enableRescaleOnResize') {
            this.rescaleOnResize = msg.value
        } else if (msg.code === 'test') {
            console.log(this.nodes)
        } else {
            console.log("msg cannot be read: " + msg)
        }
    },

    deleteNodeById: function (nodeId) {
        for (let i = 0; i < this.nodes.length; i++) {
            if (this.nodes[i].id === nodeId) {
                this.nodes.splice(i, 1);
                break
            }
        }

        this.model.unset('nodes')
        this.model.set('nodes', this.nodes)
        this.model.save_changes()

        d3.select(this.svg)
            .selectAll(".node")
            .filter(function (d) {
                return d.id === nodeId;
            }).remove()

        d3.select(this.svg)
            .selectAll("text")
            .filter(function (d) {
                return d.id === nodeId;
            }).remove()
    },

    deleteLinkById: function (linkId) {
        for (let i = this.links.length - 1; i >= 0; i--) {
            if (this.links[i].id === linkId) {
                this.links.splice(i, 1);
            }
        }

        this.model.unset('links')
        this.model.set('links', this.links)
        this.model.save_changes()

        d3.select(this.svg)
            .selectAll(".line")
            .filter(function (d) {
                return d.id === linkId;
            }).remove()
    },

    clearGraph: function () {
        this.nodes = []
        this.links = []

        this.model.unset('nodes')
        this.model.set('nodes', this.nodes)
        this.model.unset('links')
        this.model.set('links', this.links)
        this.model.save_changes()

        d3.select(this.svg).selectAll(".node").remove()
        d3.select(this.svg).selectAll("text").remove()
        d3.select(this.svg).selectAll(".line").remove()
    },

    getBoundingBox: function (nodes, links) {
        var boundingbox = {
            "minX": Number.MAX_VALUE,
            "maxX": Number.MIN_VALUE,
            "minY": Number.MAX_VALUE,
            "maxY": Number.MIN_VALUE,
        }

        for (let i = 0; i < nodes.length; i++) {
            if (nodes[i].x < boundingbox.minX) boundingbox.minX = nodes[i].x
            if (nodes[i].x > boundingbox.maxX) boundingbox.maxX = nodes[i].x

            if (nodes[i].y < boundingbox.minY) boundingbox.minY = nodes[i].y
            if (nodes[i].y > boundingbox.maxY) boundingbox.maxY = nodes[i].y
        }

        for (let i = 0; i < links.length; i++) {
            for (let j = 0; j < links[i].bends.length; j++) {
                let bend = links[i].bends[j]

                if (bend[0] < boundingbox.minX) boundingbox.minX = bend[0]
                if (bend[0] > boundingbox.maxX) boundingbox.maxX = bend[0]

                if (bend[1] < boundingbox.minY) boundingbox.minY = bend[1]
                if (bend[1] > boundingbox.maxY) boundingbox.maxY = bend[1]
            }
        }

        return boundingbox
    },

    removeBendMovers: function () {
        d3.select(this.svg).selectAll(".bendMover_holder").remove()
    },

    // Defines how the widget gets rendered into the DOM
    render: function () {
        //used for initial data and reloading the widget
        this.nodes = this.model.get('nodes')
        this.links = this.model.get('links')

        if (this.el.childNodes.length === 0) {
            let svgId = "G" + Math.random().toString(16).slice(2)

            this.svg = document.createElementNS("http://www.w3.org/2000/svg", "svg")
            this.svg.setAttribute("id", svgId)
            this.svg.setAttribute("width", this.width);
            this.svg.setAttribute("height", this.height);

            this.el.appendChild(this.svg)
        }

        if (this.nodes != null && this.links != null) {
            this.draw_graph(this.nodes, this.links)
        }
    },

    draw_graph(nodes_data, links_data) {
        let widgetView = this

        const svg = d3.select(this.svg)

        svg.on("click", function (event) {
            if (event.path[0].className.animVal !== "line" && event.path[0].className.animVal !== "bendMover") {
                widgetView.removeBendMovers()
            }
        })

        let radius = 15;

        const line = d3.line()

        d3.select(".everything").remove()
        //add encompassing group for the zoom
        this.g = svg.append("g").attr("class", "everything");
        let g = this.g

        let clickThickness = 10


        constructArrowElements()
        constructLinkElements(links_data)
        constructLinkClickElements(links_data)
        constructNodeElements(nodes_data)
        constructTextElements(nodes_data)

        function constructArrowElements() {
            //construct arrow for circle
            svg.append("svg:defs").selectAll("marker")
                .data(["endCircle"])
                .enter().append("svg:marker")
                .attr("id", String)
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", radius * 4 / 3 + 8)
                .attr("refY", 0)
                .attr("markerWidth", 8)
                .attr("markerHeight", 8)
                .attr("orient", "auto")
                .attr("fill", "black")
                .append("svg:path")
                .attr("d", "M0,-5L10,0L0,5");

            //construct arrow for square
            svg.append("svg:defs").selectAll("marker")
                .data(["endSquare"])
                .enter().append("svg:marker")
                .attr("id", String)
                .attr("viewBox", "0 -5 10 10")
                .attr("refX", (Math.sqrt(8 * radius * radius) / 2) * 4 / 3 + 8)
                .attr("refY", 0)
                .attr("markerWidth", 8)
                .attr("markerHeight", 8)
                .attr("orient", "auto")
                .attr("fill", "black")
                .append("svg:path")
                .attr("d", "M0,-5L10,0L0,5");
        }

        function constructLinkElements(links_data) {
            return g.append("g")
                .attr("class", "line_holder")
                .selectAll(".line")
                .data(links_data)
                .enter()
                .append("path")
                .attr("class", "line")
                .attr("id", function (d) {
                    return d.id
                })
                .attr("marker-end", function (d) {
                    if (d.arrow && d.t_shape === 0) {
                        return "url(#endSquare)";
                    } else if (d.arrow && d.t_shape !== 0) {
                        return "url(#endCircle)";
                    } else {
                        return null;
                    }
                })
                .attr("d", function (d) {
                    let points = [[d.sx, d.sy]].concat(d.bends).concat([[d.tx, d.ty]])
                    return line(points)
                })
                .attr("stroke", function (d) {
                    return getColorStringFromJson(d.strokeColor)
                })
                .attr("stroke-width", function (d) {
                    return d.strokeWidth
                })
                .attr("fill", "none");
        }

        function constructLinkClickElements(links_data) {
            return g.append("g")
                .attr("class", "line_click_holder")
                .selectAll(".line")
                .data(links_data)
                .enter()
                .append("path")
                .attr("class", "line")
                .attr("id", function (d) {
                    return d.id
                })
                .attr("d", function (d) {
                    let points = [[d.sx, d.sy]].concat(d.bends).concat([[d.tx, d.ty]])
                    return line(points)
                })
                .attr("stroke", "transparent")
                .attr("stroke-width", function (d) {
                    return Math.max(d.strokeWidth, clickThickness)
                })
                .attr("fill", "none")
                .on("click", function (event, d) {
                    widgetView.send({"code": "linkClicked", "id": event.target.__data__.id});

                    if (!widgetView.isBendMovementEnabled) return
                    widgetView.removeBendMovers()

                    const bendMoverData = []

                    for (let i = 0; i < d.bends.length; i++) {
                        bendMoverData.push({
                            "id": d.id,
                            "x": d.bends[i][0],
                            "y": d.bends[i][1],
                            "bendIndex": i,
                            "strokeWidth": 1
                        })
                    }

                    let bendMovers = g.append("g")
                        .attr("class", "bendMover_holder")
                        .selectAll(".bendMover")
                        .data(bendMoverData)
                        .enter()
                        .append("circle")
                        .attr("class", "bendMover")
                        .attr("cx", function (d) {
                            return d.x
                        })
                        .attr("cy", function (d) {
                            return d.y
                        })
                        .attr("id", function (d) {
                            return d.id
                        })
                        .attr("r", 7)
                        .attr("fill", "yellow")
                        .attr("stroke", "black")
                        .attr("stroke-width", function (d) {
                            return d.strokeWidth
                        })

                    const drag_handler_bends = d3.drag()
                        .on("start", dragstarted_bends)
                        .on("drag", dragged_bends)
                        .on("end", dragended_bends);

                    bendMovers.call(drag_handler_bends);
                });
        }

        function constructNodeElements(nodes_data) {
            return g.append("g")
                .attr("class", "node_holder")
                .selectAll(".node")
                .data(nodes_data)
                .enter()
                .append(function (d) {
                    if (d.shape === 0) {
                        return document.createElementNS("http://www.w3.org/2000/svg", "rect");
                    } else {
                        return document.createElementNS("http://www.w3.org/2000/svg", "circle");
                    }
                })
                .attr("class", "node")
                .attr("width", function (d) {
                    return d.nodeWidth
                })
                .attr("height", function (d) {
                    return d.nodeHeight
                })
                .attr("x", function (d) {
                    return d.x - d.nodeWidth / 2
                })
                .attr("y", function (d) {
                    return d.y - d.nodeHeight / 2
                })
                .attr("cx", function (d) {
                    return d.x
                })
                .attr("cy", function (d) {
                    return d.y
                })
                .attr("id", function (d) {
                    return d.id
                })
                .attr("r", function (d) {
                    return d.nodeHeight / 2
                })
                .attr("fill", function (d) {
                    return getColorStringFromJson(d.fillColor)
                })
                .attr("stroke", function (d) {
                    return getColorStringFromJson(d.strokeColor)
                })
                .attr("stroke-width", function (d) {
                    return d.strokeWidth
                })
                .on("click", function (event) {
                    if (!widgetView.isNodeMovementEnabled) {
                        widgetView.send({"code": "nodeClicked", "id": event.target.__data__.id});
                    }
                });
        }

        function constructTextElements(nodes_data) {
            return g.append("g")
                .attr("class", "texts")
                .selectAll("text")
                .data(nodes_data)
                .enter()
                .append("text")
                .attr("text-anchor", "middle")
                .attr("dominant-baseline", "central")
                .attr("fill", "black")
                .attr("stroke-width", 1)
                .attr("stroke", "white")
                .attr("paint-order", "stroke")
                .attr("id", function (d) {
                    return d.id
                })
                .text(function (d) {
                    return d.name;
                })
                .attr("transform", function (d) { //<-- use transform it's not a g
                    return "translate(" + d.x + "," + d.y + ")";
                })
                .on("click", function (event) {
                    if (!widgetView.isNodeMovementEnabled) {
                        widgetView.send({"code": "nodeClicked", "id": event.target.__data__.id});
                    }
                });
        }

        function getColorStringFromJson(color) {
            return "rgba(" + color.r + ", " + color.g + ", " + color.b + ", " + color.a + ")"
        }

        this.readjustZoomLevel(this.getInitialTransform(radius))

        //add drag capabilities
        widgetView.drag_handler = d3.drag()
            .on("start", dragstarted_nodes)
            .on("drag", dragged_nodes)
            .on("end", dragended_nodes);

        //Drag functions for nodes
        function dragstarted_nodes(event, d) {
            const nodeId = this.id

            d3.select(widgetView.svg)
                .selectAll(".node")
                .filter(function (data) {
                    return data.id === nodeId;
                })
                .attr("stroke-width", function (data) {
                    return data.strokeWidth + 1
                });
        }

        function dragged_nodes(event, d) {
            const nodeId = this.id

            d3.select(widgetView.svg)
                .selectAll(".node")
                .filter(function (data) {
                    return data.id === nodeId;
                })
                .attr("cx", event.x)
                .attr("cy", event.y)
                .attr("x", event.x - d.nodeWidth/2)
                .attr("y", event.y - d.nodeHeight/2);

            d3.select(widgetView.svg)
                .selectAll("text")
                .filter(function (data) {
                    return data.id === nodeId;
                })
                .attr("transform", function (d) { //<-- use transform it's not a g
                    return "translate(" + event.x + "," + event.y + ")";
                });

            d3.select(widgetView.svg)
                .selectAll(".line")
                .filter(function (data) {
                    return data.s_id === nodeId;
                })
                .attr("d", function (d) {
                    d.sx = event.x
                    d.sy = event.y
                    let points = [[d.sx, d.sy]].concat(d.bends).concat([[d.tx, d.ty]])
                    return line(points)
                })

            d3.select(widgetView.svg)
                .selectAll(".line")
                .filter(function (data) {
                    return data.t_id === nodeId;
                })
                .attr("d", function (d) {
                    d.tx = event.x
                    d.ty = event.y
                    let points = [[d.sx, d.sy]].concat(d.bends).concat([[d.tx, d.ty]])
                    return line(points)
                })
        }

        function dragended_nodes(event, d) {
            const nodeId = this.id

            d3.select(widgetView.svg)
                .selectAll(".node")
                .filter(function (data) {
                    return data.id === nodeId;
                })
                .attr("stroke-width", function (data) {
                    return data.strokeWidth
                });

            //if node only got clicked and not moved
            if (d.x === event.x && d.y === event.y) {
                widgetView.send({"code": "nodeClicked", "id": nodeId});
            } else {
                d.x = Math.round(event.x)
                d.y = Math.round(event.y)
                widgetView.send({"code": "nodeMoved", "id": this.id, "x": d.x, "y": d.y});
            }
        }

        //Drag functions for bends
        function dragstarted_bends(event, d) {
            d3.select(widgetView.svg)
                .selectAll(".bendMover")
                .filter(function (data) {
                    return data.id === d.id && data.bendIndex === d.bendIndex;
                })
                .attr("stroke-width", function (data) {
                    return data.strokeWidth + 1
                });
        }

        function dragged_bends(event, d) {
            const edgeId = d.id
            const bendIndex = d.bendIndex

            d3.select(widgetView.svg)
                .selectAll(".bendMover")
                .filter(function (data) {
                    return data.id === edgeId && data.bendIndex === bendIndex;
                })
                .attr("cx", event.x)
                .attr("cy", event.y);

            d3.select(widgetView.svg)
                .selectAll(".line")
                .filter(function (data) {
                    return data.id === edgeId;
                })
                .attr("d", function (data) {
                    data.bends[bendIndex][0] = event.x
                    data.bends[bendIndex][1] = event.y
                    let points = [[data.sx, data.sy]].concat(data.bends).concat([[data.tx, data.ty]])
                    return line(points)
                })
        }

        function dragended_bends(event, d) {
            d3.select(widgetView.svg)
                .selectAll(".bendMover")
                .attr("stroke-width", function (data) {
                    return data.strokeWidth
                });

            //only send message if bend actually moved
            if (d.x !== event.x || d.y !== event.y) {
                d.x = Math.round(event.x)
                d.y = Math.round(event.y)
                widgetView.send({"code": "bendMoved", "edgeId": this.id, "bendIndex": d.bendIndex, "x": d.x, "y": d.y});
            }
        }
    }
});

module.exports = {
    WidgetModel: WidgetModel,
    WidgetView: WidgetView
};
