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
    })
});

// Custom View. Renders the widget model.
var WidgetView = widgets.DOMWidgetView.extend({
    initialize: function (parameters) {
        WidgetView.__super__.initialize.call(this, parameters);

        this.isCallbackAllowed = true
        this.isDragDisabled = true
        this.nodes = []
        this.links = []
        this.model.off('msg:custom')
        this.model.on('msg:custom', this.handle_msg.bind(this));

        this.model.on('change:links', this.renderCallbackCheck, this);
        this.model.on('change:links', this.renderCallbackCheck, this);
    },

    renderCallbackCheck: function () {
        if (this.isCallbackAllowed) this.render()
    },

    handle_msg: function (msg) {
        if (msg.code === 'deleteNodeById') {
            this.isCallbackAllowed = false
            this.deleteNodeById(msg.data)
            this.isCallbackAllowed = true
        } else if (msg.code === 'deleteLinkById') {
            this.isCallbackAllowed = false
            this.deleteLinkById(msg.data)
            this.isCallbackAllowed = true
        } else if (msg.code === 'clearGraph') {
            this.isCallbackAllowed = false
            this.clearGraph()
            this.isCallbackAllowed = true
        } else if (msg.code === 'enableNodeMovement') {
            this.isDragDisabled = !msg.value

            if (this.isDragDisabled) {
                d3.select(this.svg).selectAll(".node").on('mousedown.drag', null);
                d3.select(this.svg).selectAll("text").on('mousedown.drag', null);
            } else {
                d3.select(this.svg).selectAll(".node").call(this.drag_handler)
                d3.select(this.svg).selectAll("text").call(this.drag_handler)
            }
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
            .selectAll("line")
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
        d3.select(this.svg).selectAll("line").remove()
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
            if (links[i].sx < boundingbox.minX) boundingbox.minX = links[i].sx
            if (links[i].tx < boundingbox.minX) boundingbox.minX = links[i].tx
            if (links[i].sx > boundingbox.maxX) boundingbox.maxX = links[i].sx
            if (links[i].tx > boundingbox.maxX) boundingbox.maxX = links[i].tx

            if (links[i].sy < boundingbox.minY) boundingbox.minY = links[i].sy
            if (links[i].ty < boundingbox.minY) boundingbox.minY = links[i].ty
            if (links[i].sy > boundingbox.maxY) boundingbox.maxY = links[i].sy
            if (links[i].ty > boundingbox.maxY) boundingbox.maxY = links[i].ty
        }

        return boundingbox
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
            this.svg.setAttribute("width", "500");
            this.svg.setAttribute("height", "500");

            this.el.appendChild(this.svg)
        }

        if (this.nodes != null && this.links != null) {
            this.draw_graph(this.nodes, this.links)
        }
    },

    draw_graph(nodes_data, links_data) {
        let widgetView = this

        let svg = d3.select(this.svg),
            width = +svg.attr("width"),
            height = +svg.attr("height");

        let radius = 15;

        let boundingBox = this.getBoundingBox(nodes_data, links_data)

        function getColorStringFromJson(color) {
            return "rgba(" + color.r + ", " + color.g + ", " + color.b + ", " + color.a + ")"
        }

        function getInvertedColorStringFromJson(color) {
            const cloneColor = JSON.parse(JSON.stringify(color));
            cloneColor.r = 255 - color.r
            cloneColor.g = 255 - color.g
            cloneColor.b = 255 - color.b
            return getColorStringFromJson(cloneColor)
        }

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

        //add encompassing group for the zoom
        let g = svg.append("g").attr("class", "everything");

        let links = g.append("g")
            .attr("class", "link")
            .selectAll("line")
            .data(links_data)
            .enter()
            .append("line")
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
            .attr("x1", function (d) {
                return d.sx
            })
            .attr("y1", function (d) {
                return d.sy
            })
            .attr("x2", function (d) {
                return d.tx
            })
            .attr("y2", function (d) {
                return d.ty
            })
            .attr("stroke", function (d) {
                return getColorStringFromJson(d.strokeColor)
            })
            .attr("stroke-width", function (d) {
                return d.strokeWidth
            })
            .on("click", function (event) {
                widgetView.send({"code": "linkClicked", "id": event.target.__data__.id});
            });

        let nodes = g.append("g")
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
            .attr("width", radius * 2)
            .attr("height", radius * 2)
            .attr("x", function (d) {
                return d.x - radius
            })
            .attr("y", function (d) {
                return d.y - radius
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
            .attr("r", radius)
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
                if (widgetView.isDragDisabled) {
                    widgetView.send({"code": "nodeClicked", "id": event.target.__data__.id});
                }
            });

        let text = g.append("g")
            .attr("class", "texts")
            .selectAll("text")
            .data(nodes_data)
            .enter()
            .append("text")
            .attr("text-anchor", "middle")
            .attr("dominant-baseline", "central")
            .attr("fill", function (d) {
                return getInvertedColorStringFromJson(d.fillColor)
            })
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
                if (widgetView.isDragDisabled) {
                    widgetView.send({"code": "nodeClicked", "id": event.target.__data__.id});
                }
            });


        //add zoom capabilities
        const zoom = d3.zoom();

        const boundingBoxWidth = boundingBox.maxX - boundingBox.minX + radius * 2
        const boundingBoxHeight = boundingBox.maxY - boundingBox.minY + radius * 2

        let scale = Math.min(width / boundingBoxWidth, height / boundingBoxHeight);
        let x = width / 2 - (boundingBox.minX + boundingBoxWidth / 2 - radius) * scale;
        let y = height / 2 - (boundingBox.minY + boundingBoxHeight / 2 - radius) * scale;

        if (nodes_data.length === 1) {
            scale = 1
            x = width / 2 - nodes_data[0].x
            y = height / 2 - nodes_data[0].y
        }

        const initialTransform = d3.zoomIdentity.translate(x, y).scale(scale)

        svg.call(zoom.transform, initialTransform)
        svg.call(zoom.on('zoom', zoomed));
        svg.call(zoom)
        g.attr("transform", initialTransform)

        function zoomed({transform}) {
            g.attr("transform", transform);
        }

        //add drag capabilities
        widgetView.drag_handler = d3.drag()
            .on("start", dragstarted)
            .on("drag", dragged)
            .on("end", dragended);

        //Drag functions
        function dragstarted(event, d) {
            const nodeId = this.id
            d3.select(this).raise().attr("stroke-width", d.strokeWidth == null ? 1 : d.strokeWidth + 1);

            d3.select("svg")
                .selectAll(".node")
                .filter(function (data) {
                    return data.id === nodeId;
                })
                .attr("stroke-width", function (data) {
                    return data.strokeWidth + 1
                });
        }

        function dragged(event, d) {
            const nodeId = this.id

            d3.select("svg")
                .selectAll(".node")
                .filter(function (data) {
                    return data.id === nodeId;
                })
                .attr("cx", event.x)
                .attr("cy", event.y)
                .attr("x", event.x - 15)
                .attr("y", event.y - 15);

            d3.select("svg")
                .selectAll("text")
                .filter(function (data) {
                    return data.id === nodeId;
                })
                .attr("transform", function (d) { //<-- use transform it's not a g
                    return "translate(" + event.x + "," + event.y + ")";
                });

            d3.select("svg")
                .selectAll("line")
                .filter(function (data) {
                    return data.s_id === nodeId && data.touchingSource;
                })
                .attr("x1", function (data) {
                    return data.sx = event.x;
                })
                .attr("y1", function (data) {
                    return data.sy = event.y;
                })

            d3.select("svg")
                .selectAll("line")
                .filter(function (data) {
                    return data.t_id === nodeId && data.touchingTarget;
                })
                .attr("x2", function (data) {
                    return data.tx = event.x;
                })
                .attr("y2", function (data) {
                    return data.ty = event.y;
                })
        }

        function dragended(event, d) {
            const nodeId = this.id

            d3.select("svg")
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
                d.x = event.x
                d.y = event.y
                widgetView.send({"code": "nodeMoved", "id": this.id, "x": d.x, "y": d.y});
            }
        }
    }
});


module.exports = {
    WidgetModel: WidgetModel,
    WidgetView: WidgetView
};
