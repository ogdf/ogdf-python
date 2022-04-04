let widgets = require('@jupyter-widgets/base');
let _ = require('lodash');
let d3 = require("d3");
require("./style.css");
//import {constructLink} from "./graph-element-constructor.mjs";

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
let WidgetModel = widgets.DOMWidgetModel.extend({
    defaults: _.extend(widgets.DOMWidgetModel.prototype.defaults(), {
        _model_name: 'WidgetModel',
        _view_name: 'WidgetView',
        _model_module: 'ogdf-python-widget',
        _view_module: 'ogdf-python-widget',
        _model_module_version: '0.1.0',
        _view_module_version: '0.1.0',
        width: 960,
        height: 540,
        x_pos: 0,
        y_pos: 0,
        zoom: 1,
        click_thickness: 10,
        animation_duration: 1000,
        force_config: null,
        rescale_on_resize: true,
    })
});

// Custom View. Renders the widget model.
let WidgetView = widgets.DOMWidgetView.extend({
    initialize: function (parameters) {
        WidgetView.__super__.initialize.call(this, parameters);

        this.isNodeMovementEnabled = this.model.get("node_movement_enabled")

        //only for internal use
        this.isTransformCallbackAllowed = true

        this.forceDirected = false

        this.clickThickness = this.model.get("click_thickness")
        this.animationDuration = this.model.get("animation_duration")
        this.gridSize = this.model.get('grid_size');

        this.nodes = []
        this.links = []

        this.width = this.model.get('width')
        this.height = this.model.get('height')

        this.model.on('msg:custom', this.handle_msg.bind(this));

        this.model.on('change:x_pos', this.transformCallbackCheck, this);
        this.model.on('change:y_pos', this.transformCallbackCheck, this);
        this.model.on('change:zoom', this.transformCallbackCheck, this);

        this.model.on('change:width', this.svgSizeChanged, this)
        this.model.on('change:height', this.svgSizeChanged, this)

        this.model.on('change:click_thickness', this.clickThicknessChanged, this)

        this.model.on('change:animation_duration', this.animationDurationChanged, this)

        this.model.on('change:grid_size', this.gridSizeChanged, this)

        this.model.on('change:force_config', this.forceConfigChanged, this)

        this.model.on('change:node_movement_enabled', this.nodeMovementChanged, this)

        this.ticksSinceSync = 0

        this.send({"code": "widgetReady"})
    },

    startForceLayout: function (forceConfig) {
        let widgetView = this

        this.forceDirected = true
        d3.select(this.svg).selectAll(".node").remove()
        d3.select(this.svg).selectAll("text").remove()
        d3.select(this.svg).selectAll(".line").remove()

        for (let i = 0; i < this.links.length; i++) {
            this.constructForceLink(this.links[i], this.line_holder, this, false)
        }

        for (let i = 0; i < this.nodes.length; i++) {
            this.constructNode(this.nodes[i], this.node_holder, this.text_holder, this, false)
        }

        setTimeout(function () {
            widgetView.rescaleAllText()
        }, 10)

        this.simulation = d3.forceSimulation().nodes(this.nodes)
            .on('end', function () {
                widgetView.syncBackend()
            });

        let link_force = d3.forceLink(this.links).id(function (d) {
            return d.id;
        });

        let charge_force = d3.forceManyBody().strength(forceConfig.chargeForce);

        let center_force = d3.forceCenter(forceConfig.forceCenterX, forceConfig.forceCenterY);

        this.simulation
            .force("charge_force", charge_force)
            .force("center_force", center_force)
            .force("links", link_force);

        //add tick instructions:
        this.simulation.on("tick", tickActions);

        if (forceConfig.fixStartPosition) {
            d3.select(this.svg).selectAll(".node")
                .attr("x", function (d) {
                    d.fx = d.x
                    d.fy = d.y
                })
        }

        function tickActions() {
            d3.select(widgetView.svg)
                .selectAll(".node")
                .attr("x", function (d) {
                    return d.x - d.nodeWidth / 2;
                })
                .attr("y", function (d) {
                    return d.y - d.nodeHeight / 2;
                })
                .attr("cx", function (d) {
                    return d.x;
                })
                .attr("cy", function (d) {
                    return d.y;
                });

            d3.select(widgetView.svg)
                .selectAll(".nodeLabel")
                .attr("transform", function (d) {
                    return "translate(" + d.x + "," + d.y + ")";
                });

            d3.select(widgetView.svg)
                .selectAll(".line")
                .attr("x1", function (d) {
                    return d.source.x;
                })
                .attr("y1", function (d) {
                    return d.source.y;
                })
                .attr("x2", function (d) {
                    return d.target.x;
                })
                .attr("y2", function (d) {
                    return d.target.y;
                })
                .attr("d", function (d) {
                    if (d.source === d.target) {
                        return widgetView.getPath(d.source.x, d.source.y, d.target.x, d.target.y)
                    }
                });

            if (widgetView.ticksSinceSync % 5 === 0) {
                widgetView.syncBackend()
                widgetView.ticksSinceSync = 0
            }
        }
    },

    stopForceLayout: function () {
        if (!this.forceDirected) return

        this.forceDirected = false;
        if (this.simulation != null) {
            this.simulation.stop()
            this.simulation = null
        }
    },

    forceConfigChanged: function () {
        let forceConfig = this.model.get("force_config")

        if (forceConfig.stop || forceConfig.stop == null) {
            this.stopForceLayout()
        } else {
            this.startForceLayout(forceConfig)
        }
    },

    nodeMovementChanged: function () {
        this.isNodeMovementEnabled = this.model.get("node_movement_enabled")

        if (!this.isNodeMovementEnabled) {
            d3.select(this.svg).selectAll(".node").on('mousedown.drag', null)
            d3.select(this.svg).selectAll(".nodeLabel").on('mousedown.drag', null)
        } else {
            d3.select(this.svg).selectAll(".node").call(this.node_drag_handler)
            d3.select(this.svg).selectAll(".nodeLabel").call(this.node_drag_handler)
        }
    },

    syncBackend: function () {
        this.send({'code': 'positionUpdate', 'nodes': this.nodes})
    },

    animationDurationChanged: function () {
        this.animationDuration = this.model.get("animation_duration")
    },

    gridSizeChanged: function () {
        this.gridSize = this.model.get('grid_size');
    },

    clickThicknessChanged: function () {
        this.clickThickness = this.model.get("click_thickness")
        let widgetView = this

        d3.select(this.svg).selectAll(".line_click_holder > .line")
            .attr("stroke-width", function (d) {
                return Math.max(d.strokeWidth, widgetView.clickThickness)
            })
    },

    svgSizeChanged: function () {
        this.width = this.model.get('width')
        this.height = this.model.get('height')

        d3.select(this.svg)
            .attr("width", this.model.get('width'))
            .attr("height", this.model.get('height'))

        if (this.model.get("rescale_on_resize")) this.readjustZoomLevel(this.getInitialTransform(15))
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
        svg.call(zoom.on('zoom', zoomed).on('end', zoomEnded));
        svg.call(zoom)
        this.g.attr("transform", transform)
        this.updateZoomLevelInModel(transform)

        function zoomed({transform}) {
            widgetView.g.attr("transform", transform);
        }

        function zoomEnded({transform}) {
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
        }
    },

    handle_msg: function (msg) {
        if (msg.code === 'clearGraph') {
            this.clearGraph()
        } else if (msg.code === 'initGraph') {
            this.links = msg.links
            this.nodes = msg.nodes
            this.render()
        } else if (msg.code === 'nodeAdded') {
            this.addNode(msg.data)
        } else if (msg.code === 'linkAdded') {
            this.addLink(msg.data)
        } else if (msg.code === 'deleteNodeById') {
            this.deleteNodeById(msg.data)
        } else if (msg.code === 'deleteLinkById') {
            this.deleteLinkById(msg.data)
        } else if (msg.code === 'updateNode') {
            this.updateNode(msg.data, msg.animated)
        } else if (msg.code === 'updateLink') {
            this.updateLink(msg.data, msg.animated)
        } else if (msg.code === 'moveLink') {
            this.moveLinkBends(msg.data)
        } else if (msg.code === 'removeAllBendMovers') {
            this.removeAllBendMovers()
        } else if (msg.code === 'removeBendMoversFor') {
            this.removeBendMoversForLink(msg.data)
        } else if (msg.code === 'downloadSvg') {
            this.downloadSvg(msg.fileName)
        } else if (msg.code === 'test') {
            this.rescaleAllText()
        } else {
            console.log("msg cannot be read: " + msg)
        }
    },

    downloadSvg: function (fileName) {
        var svgData = this.svg.outerHTML;
        if (!svgData.match(/^<svg[^>]+xmlns="http\:\/\/www\.w3\.org\/2000\/svg"/)) {
            svgData = svgData.replace(/^<svg/, '<svg xmlns="http://www.w3.org/2000/svg"');
        }
        if (!svgData.match(/^<svg[^>]+"http\:\/\/www\.w3\.org\/1999\/xlink"/)) {
            svgData = svgData.replace(/^<svg/, '<svg xmlns:xlink="http://www.w3.org/1999/xlink"');
        }
        var svgBlob = new Blob([svgData], {type: "image/svg+xml;charset=utf-8"});
        var svgUrl = URL.createObjectURL(svgBlob);
        var downloadLink = document.createElement("a");
        downloadLink.href = svgUrl;
        downloadLink.download = fileName + ".svg";
        downloadLink.click();
    },

    moveLinkBends: function (d) {
        const line = d3.line()
        let widgetView = this
        let bendMoverData = []

        for (let i = 0; i < d.bends.length; i++) {
            bendMoverData.push({
                "id": d.id,
                "x": d.bends[i][0],
                "y": d.bends[i][1],
                "bendIndex": i,
                "strokeWidth": 1
            })
        }

        let bendMovers = this.bendMover_holder
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
            .on("start", dragStarted_bends)
            .on("drag", dragged_bends)
            .on("end", dragEnded_bends);

        bendMovers.call(drag_handler_bends);

        //Drag functions for bends
        function dragStarted_bends(event, d) {
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

            if (bendIndex === 0) {
                d3.select(widgetView.svg)
                    .selectAll(".linkLabel")
                    .filter(function (data) {
                        return data.id === edgeId;
                    })
                    .attr("transform", function () { //<-- use transform it's not a g
                        return "translate(" + event.x + "," + event.y + ")";
                    });
            }
        }

        function dragEnded_bends(event, d) {
            d3.select(widgetView.svg)
                .selectAll(".bendMover")
                .attr("stroke-width", function (data) {
                    return data.strokeWidth
                });

            //only send message if bend actually moved
            if (d.x !== event.x || d.y !== event.y) {
                d.x = Math.round(event.x)
                d.y = Math.round(event.y)
                widgetView.send({"code": "bendMoved", "linkId": this.id, "bendIndex": d.bendIndex, "x": d.x, "y": d.y});
            } else {
                //ctrl key not possible because it doesnt activate the drag
                widgetView.send({
                    "code": "bendClicked",
                    "linkId": this.id,
                    "bendIndex": d.bendIndex,
                    "altKey": event.sourceEvent.altKey
                });
            }
        }
    },

    addNode: function (node) {
        if (this.forceDirected) this.stopForceLayout()
        this.nodes.push(node)
        this.constructNode(node, this.node_holder, this.text_holder, this, false)
        this.forceConfigChanged()
    },

    addLink: function (link) {
        if (this.forceDirected) this.stopForceLayout()
        this.links.push(link)
        this.constructLink(link, this.line_holder, this.line_text_holder, this.line_click_holder, this, this.clickThickness, false)
        this.forceConfigChanged()
    },

    deleteNodeById: function (nodeId) {
        if (this.forceDirected) this.stopForceLayout()
        for (let i = 0; i < this.nodes.length; i++) {
            if (this.nodes[i].id === nodeId) {
                this.nodes.splice(i, 1);
                break
            }
        }

        d3.select(this.svg)
            .selectAll(".node")
            .filter(function (d) {
                return d.id === nodeId;
            }).remove()

        d3.select(this.svg)
            .selectAll(".nodeLabel")
            .filter(function (d) {
                return d.id === nodeId;
            }).remove()

        this.forceConfigChanged()
    },

    deleteLinkById: function (linkId) {
        if (this.forceDirected) this.stopForceLayout()
        for (let i = this.links.length - 1; i >= 0; i--) {
            if (this.links[i].id === linkId) {
                this.links.splice(i, 1);
            }
        }

        d3.select(this.svg)
            .selectAll(".line")
            .filter(function (d) {
                return d.id === linkId;
            }).remove()

        d3.select(this.svg)
            .selectAll(".linkLabel")
            .filter(function (d) {
                return d.id === linkId;
            }).remove()

        this.forceConfigChanged()
    },

    updateNode: function (node, animated) {
        let widgetView = this

        let n = d3.select(this.svg)
            .selectAll(".node")
            .filter(function (d) {
                return d.id === node.id;
            })

        let nl = d3.select(this.svg)
            .selectAll(".nodeLabel")
            .filter(function (d) {
                return d.id === node.id;
            })

        if (widgetView.forceDirected) widgetView.simulation.alphaTarget(0.3).restart()

        n.transition()
            .duration(animated ? this.animationDuration : 1)
            .attr("width", function (d) {
                d.nodeWidth = node.nodeWidth
                return d.nodeWidth
            })
            .attr("height", function (d) {
                d.nodeHeight = node.nodeHeight
                return d.nodeHeight
            })
            .attr("x", function (d) {
                if (widgetView.forceDirected && !widgetView.isNodeMovementEnabled)
                    d.fx = node.x
                else if (widgetView.forceDirected)
                    return

                d.x = node.x
                return d.x - d.nodeWidth / 2
            })
            .attr("y", function (d) {
                if (widgetView.forceDirected && !widgetView.isNodeMovementEnabled)
                    d.fy = node.y
                else if (widgetView.forceDirected)
                    return

                d.y = node.y
                return d.y - d.nodeHeight / 2
            })
            .attr("cx", function (d) {
                if (widgetView.forceDirected && !widgetView.isNodeMovementEnabled)
                    d.fx = node.x
                else if (widgetView.forceDirected)
                    return

                d.x = node.x
                return d.x
            })
            .attr("cy", function (d) {
                if (widgetView.forceDirected && !widgetView.isNodeMovementEnabled)
                    d.fy = node.y
                else if (widgetView.forceDirected)
                    return

                d.y = node.y
                return d.y
            })
            .attr("r", function (d) {
                d.nodeHeight = node.nodeHeight
                return d.nodeHeight / 2
            })
            .attr("fill", function (d) {
                d.fillColor = node.fillColor
                return widgetView.getColorStringFromJson(d.fillColor)
            })
            .attr("stroke", function (d) {
                d.strokeColor = node.strokeColor
                return widgetView.getColorStringFromJson(d.strokeColor)
            })
            .attr("stroke-width", function (d) {
                d.strokeWidth = node.strokeWidth
                return d.strokeWidth
            })

        if (widgetView.forceDirected) {
            setTimeout(function () {
                widgetView.simulation.alphaTarget(0)
            }, 1000)
        }

        let textChanged = true
        nl.text(function (d) {
            if (d.name !== node.name) {
                d.name = node.name
            } else {
                textChanged = false
            }
            return d.name;
        })

        if (textChanged) {
            setTimeout(function () {
                widgetView.rescaleTextById(node.id)
            }, 10)
        }

        nl.transition()
            .duration(animated ? this.animationDuration : 1)
            .attr("transform", function (d) { //<-- use transform it's not a g
                if (widgetView.forceDirected && widgetView.isNodeMovementEnabled)
                    return

                d.x = node.x
                d.y = node.y
                return "translate(" + d.x + "," + d.y + ")";
            })
    },

    addBendsToLink: function (link, totalBendAmount) {
        let points = [[link.sx, link.sy]].concat(link.bends).concat([[link.tx, link.ty]])

        while (totalBendAmount > points.length - 2) {
            for (let i = points.length - 2; i >= 0 && totalBendAmount > points.length - 2; i--) {
                let newPoint = [(points[i][0] + points[i + 1][0]) / 2, (points[i][1] + points[i + 1][1]) / 2]
                points.splice(i + 1, 0, newPoint);
            }
        }

        points.shift()
        points.pop()

        link.bends = points

        return link
    },

    updateLink: function (link, animated) {
        let bendMoverActive = false
        d3.select(this.svg)
            .selectAll(".bendMover")
            .filter(function (d) {
                if (d.id === link.id) bendMoverActive = true
                return d.id === link.id;
            }).remove()

        if (bendMoverActive)
            this.moveLinkBends(link)

        if (!animated) {
            this.deleteLinkById(link.id)
            this.addLink(link)
            return
        }

        //artificially add bends to make animation better
        let currentLink
        for (let i = this.links.length - 1; i >= 0; i--) {
            if (this.links[i].id === link.id) {
                currentLink = this.links[i]
            }
        }

        let paddedLink = null
        if (currentLink !== null && currentLink.bends.length !== link.bends.length) {
            if (currentLink.bends.length < link.bends.length) {
                this.deleteLinkById(link.id)
                this.addLink(this.addBendsToLink(JSON.parse(JSON.stringify(currentLink)), link.bends.length))
            } else {
                paddedLink = this.addBendsToLink(JSON.parse(JSON.stringify(link)), currentLink.bends.length)
            }
        }

        let widgetView = this
        const line = d3.line()

        let l = d3.select(this.svg)
            .selectAll(".line_holder > .line")
            .filter(function (d) {
                return d.id === link.id;
            })

        let lc = d3.select(this.svg)
            .selectAll(".line_click_holder > .line")
            .filter(function (d) {
                return d.id === link.id;
            })

        let ll = d3.select(this.svg)
            .selectAll(".linkLabel")
            .filter(function (d) {
                return d.id === link.id;
            })

        l.transition()
            .duration(this.animationDuration)
            .attr("d", function (d) {
                let newLink = paddedLink == null ? link : paddedLink
                d.sx = newLink.sx
                d.sy = newLink.sy
                d.bends = newLink.bends
                d.tx = newLink.tx
                d.ty = newLink.ty

                if (d.source === d.target && d.bends.length === 0) {
                    return widgetView.getPath(d.sx, d.sy, d.tx, d.ty)
                }

                let points = [[d.sx, d.sy]].concat(d.bends).concat([[d.tx, d.ty]])
                return line(points)
            })
            .attr("stroke", function (d) {
                d.strokeColor = link.strokeColor
                return widgetView.getColorStringFromJson(d.strokeColor)
            })
            .attr("stroke-width", function (d) {
                d.strokeWidth = link.strokeWidth
                return d.strokeWidth
            })

        lc.transition()
            .duration(this.animationDuration)
            .attr("d", function (d) {
                d.sx = link.sx
                d.sy = link.sy
                d.bends = link.bends
                d.tx = link.tx
                d.ty = link.ty

                if (d.source === d.target && d.bends.length === 0) {
                    return widgetView.getPath(d.sx, d.sy, d.tx, d.ty)
                }

                let points = [[d.sx, d.sy]].concat(d.bends).concat([[d.tx, d.ty]])
                return line(points)
            })
            .attr("stroke-width", function (d) {
                d.strokeWidth = link.strokeWidth
                return Math.max(d.strokeWidth, widgetView.clickThickness)
            })

        ll.transition()
            .duration(this.animationDuration)
            .text(function (d) {
                d.label = link.label
                return d.label;
            })
            .attr("transform", function (d) { //<-- use transform it's not a g
                d.label_x = link.label_x
                d.label_y = link.label_y
                return "translate(" + d.label_x + "," + d.label_y + ")";
            })

        if (paddedLink != null) {
            setTimeout(() => {
                this.deleteLinkById(link.id)
                this.addLink(link)
            }, this.animationDuration);
        }
    },

    clearGraph: function () {
        this.nodes = []
        this.links = []

        d3.select(this.svg).selectAll(".node").remove()
        d3.select(this.svg).selectAll("text").remove()
        d3.select(this.svg).selectAll(".line").remove()
    },

    getBoundingBox: function (nodes, links) {
        let boundingBox = {
            "minX": Number.MAX_VALUE,
            "maxX": Number.MIN_VALUE,
            "minY": Number.MAX_VALUE,
            "maxY": Number.MIN_VALUE,
        }

        for (let i = 0; i < nodes.length; i++) {
            if (nodes[i].x < boundingBox.minX) boundingBox.minX = nodes[i].x
            if (nodes[i].x > boundingBox.maxX) boundingBox.maxX = nodes[i].x

            if (nodes[i].y < boundingBox.minY) boundingBox.minY = nodes[i].y
            if (nodes[i].y > boundingBox.maxY) boundingBox.maxY = nodes[i].y
        }

        for (let i = 0; i < links.length; i++) {
            for (let j = 0; j < links[i].bends.length; j++) {
                let bend = links[i].bends[j]

                if (bend[0] < boundingBox.minX) boundingBox.minX = bend[0]
                if (bend[0] > boundingBox.maxX) boundingBox.maxX = bend[0]

                if (bend[1] < boundingBox.minY) boundingBox.minY = bend[1]
                if (bend[1] > boundingBox.maxY) boundingBox.maxY = bend[1]
            }
        }

        return boundingBox
    },

    removeAllBendMovers: function () {
        d3.select(this.svg).selectAll(".bendMover").remove()
    },

    removeBendMoversForLink: function (linkId) {
        d3.select(this.svg)
            .selectAll(".bendMover")
            .filter(function (d) {
                return d.id === linkId;
            }).remove()
    },

    // Defines how the widget gets rendered into the DOM
    render: function () {
        if (this.links.length === 0 && this.nodes.length === 0)
            return

        if (this.el.childNodes.length === 0) {
            let svgId = "G" + Math.random().toString(16).slice(2)

            this.svg = document.createElementNS("http://www.w3.org/2000/svg", "svg")
            this.svg.setAttribute("id", svgId)
            this.svg.setAttribute("width", this.width);
            this.svg.setAttribute("height", this.height);

            this.el.appendChild(this.svg)
        }

        this.draw_graph(this.nodes, this.links)

        var widgetView = this

        setTimeout(function () {
            widgetView.rescaleAllText()
        }, 10)
    },

    constructForceLink(linkData, line_holder, widgetView, basic) {
        if (linkData.source === linkData.target) {
            line_holder
                .data([linkData])
                .enter()
                .append("path")
                .attr("class", "line")
                .attr("id", function (d) {
                    return d.id
                })
                .attr("d", function (d) {
                    return widgetView.getPath(d.sx, d.sy, d.tx, d.ty)
                })
                .attr("stroke", function (d) {
                    return widgetView.getColorStringFromJson(d.strokeColor)
                })
                .attr("stroke-width", function (d) {
                    return d.strokeWidth
                })
                .attr("fill", "none")
                .on("click", function (event, d) {
                    if (basic) return
                    widgetView.send({
                        "code": "linkClicked",
                        "id": d.id,
                        "altKey": event.altKey,
                        "ctrlKey": event.ctrlKey
                    });
                });
            return
        }

        line_holder
            .data([linkData])
            .enter()
            .append("line")
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
            .attr("x1", function (d) {
                if (d.sx == null) return
                return d.sx
            })
            .attr("y1", function (d) {
                if (d.sy == null) return
                return d.sy
            })
            .attr("x2", function (d) {
                if (d.tx == null) return
                return d.tx
            })
            .attr("y2", function (d) {
                if (d.ty == null) return
                return d.ty
            })
            .attr("stroke", function (d) {
                return widgetView.getColorStringFromJson(d.strokeColor)
            })
            .attr("stroke-width", function (d) {
                return d.strokeWidth
            })
            .attr("fill", "none")
            .on("click", function (event, d) {
                if (basic) return
                widgetView.send({"code": "linkClicked", "id": d.id, "altKey": event.altKey, "ctrlKey": event.ctrlKey});
            });
    },

    constructLink(linkData, line_holder, line_text_holder, line_click_holder, widgetView, clickThickness, basic) {
        const line = d3.line()

        line_holder
            .data([linkData])
            .enter()
            .append("path")
            .attr("class", "line")
            .attr("id", function (d) {
                return d.id
            })
            .attr("marker-end", function (d) {
                if (d.arrow && d.t_shape === 0 && d.source !== d.target) {
                    return "url(#endSquare)";
                } else if (d.arrow && d.t_shape !== 0 && d.source !== d.target) {
                    return "url(#endCircle)";
                } else {
                    return null;
                }
            })
            .attr("d", function (d) {
                if (d.source === d.target && d.bends.length === 0) {
                    return widgetView.getPath(d.sx, d.sy, d.tx, d.ty)
                }

                let points = [[d.sx, d.sy]].concat(d.bends).concat([[d.tx, d.ty]])
                return line(points)
            })
            .attr("stroke", function (d) {
                return widgetView.getColorStringFromJson(d.strokeColor)
            })
            .attr("stroke-width", function (d) {
                return d.strokeWidth
            })
            .attr("fill", "none");

        line_text_holder
            .data([linkData])
            .enter()
            .append("text")
            .attr("class", "linkLabel")
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
                return d.label;
            })
            .style("font-size", "0.5em")
            .attr("transform", function (d) { //<-- use transform it's not a g
                return "translate(" + d.label_x + "," + d.label_y + ")";
            })

        if (basic) return

        line_click_holder
            .data([linkData])
            .enter()
            .append("path")
            .attr("class", "line")
            .attr("id", function (d) {
                return d.id
            })
            .attr("d", function (d) {
                if (d.source === d.target && d.bends.length === 0) {
                    return widgetView.getPath(d.sx, d.sy, d.tx, d.ty)
                }

                let points = [[d.sx, d.sy]].concat(d.bends).concat([[d.tx, d.ty]])
                return line(points)
            })
            .attr("stroke", "transparent")
            .attr("stroke-width", function (d) {
                return Math.max(d.strokeWidth, clickThickness)
            })
            .attr("fill", "none")
            .on("click", function (event, d) {
                widgetView.send({"code": "linkClicked", "id": d.id, "altKey": event.altKey, "ctrlKey": event.ctrlKey});
            })
    },

    constructNode(nodeData, node_holder, text_holder, widgetView, basic) {
        let node = node_holder
            .data([nodeData])
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
                return widgetView.getColorStringFromJson(d.fillColor)
            })
            .attr("stroke", function (d) {
                return widgetView.getColorStringFromJson(d.strokeColor)
            })
            .attr("stroke-width", function (d) {
                return d.strokeWidth
            })
            .on("click", function (event, d) {
                if (!basic && !widgetView.isNodeMovementEnabled) {
                    widgetView.send({
                        "code": "nodeClicked",
                        "id": d.id,
                        "altKey": event.altKey,
                        "ctrlKey": event.ctrlKey
                    });
                }
            })

        let text = text_holder
            .data([nodeData])
            .enter()
            .append("text")
            .attr("class", "nodeLabel")
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
            .style("font-size", "1em")
            .attr("transform", function (d) { //<-- use transform it's not a g
                return "translate(" + d.x + "," + d.y + ")";
            })
            .on("click", function (event, d) {
                if (!basic && !widgetView.isNodeMovementEnabled) {
                    widgetView.send({
                        "code": "nodeClicked",
                        "id": d.id,
                        "altKey": event.altKey,
                        "ctrlKey": event.ctrlKey
                    });
                }
            })

        if (widgetView.isNodeMovementEnabled) {
            node.call(widgetView.node_drag_handler)
            text.call(widgetView.node_drag_handler)
        }
    },

    getColorStringFromJson(color) {
        return "rgba(" + color.r + ", " + color.g + ", " + color.b + ", " + color.a + ")"
    },

    getPath: function (x1, y1, x2, y2) {
        let xRotation = -45;
        let largeArc = 1;
        let drx = 30;
        let dry = 20;
        return "M" + x1 + "," + y1 + "A" + drx + "," + dry + " " + xRotation + "," + largeArc + "," + 1 + " " + (x2 + 1) + "," + (y2 + 1);
    },

    draw_graph(nodes_data, links_data) {
        let widgetView = this
        const svg = d3.select(this.svg)

        svg.on("click", function (event) {
            let backgroundClicked
            if (event.path === undefined) {
                backgroundClicked = event.originalTarget.nodeName === "svg"
            } else {
                backgroundClicked = event.path[0].nodeName === "svg"
            }

            widgetView.send({
                "code": "svgClicked",
                "x": event.offsetX,
                "y": event.offsetY,
                "altKey": event.altKey,
                "ctrlKey": event.ctrlKey,
                "backgroundClicked": backgroundClicked
            });
        })

        let radius = nodes_data.length > 0 ? nodes_data[0].nodeWidth / 2 : 0

        d3.select(this.svg).selectAll(".everything").remove()
        //add encompassing group for the zoom
        this.g = svg.append("g").attr("class", "everything");

        constructArrowElements(radius)

        //links
        this.line_holder = this.g.append("g")
            .attr("class", "line_holder")
            .selectAll(".line")

        this.line_click_holder = this.g.append("g")
            .attr("class", "line_click_holder")
            .selectAll(".line")

        this.line_text_holder = this.g.append("g")
            .attr("class", "line_text_holder")
            .selectAll(".lineText")

        for (let i = 0; i < links_data.length; i++) {
            widgetView.constructLink(links_data[i], this.line_holder, this.line_text_holder, this.line_click_holder, widgetView, this.clickThickness, false)
        }

        this.bendMover_holder = this.g.append("g").attr("class", "bendMover_holder").selectAll("bendMover")

        //nodes
        widgetView.node_drag_handler = d3.drag()
            .on("start", dragStarted_nodes)
            .on("drag", dragged_nodes)
            .on("end", dragEnded_nodes);

        this.node_holder = this.g.append("g")
            .attr("class", "node_holder")
            .selectAll(".node")

        this.text_holder = this.g.append("g")
            .attr("class", "text_holder")
            .selectAll(".nodeLabel")

        for (let i = 0; i < nodes_data.length; i++) {
            widgetView.constructNode(nodes_data[i], this.node_holder, this.text_holder, widgetView, false)
        }

        function constructArrowElements(radius) {
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

        this.readjustZoomLevel(this.getInitialTransform(radius))

        //Drag functions for nodes
        function dragStarted_nodes(event, d) {
            const nodeId = this.id

            d.startX = d.x
            d.startY = d.y

            //makes stroke bigger for dragged node
            d3.select(widgetView.svg)
                .selectAll(".node")
                .filter(function (data) {
                    return data.id === nodeId;
                })
                .attr("stroke-width", function (data) {
                    return data.strokeWidth + 1
                });

            if (widgetView.forceDirected && !event.active) widgetView.simulation.alphaTarget(0.3).restart();
        }

        function dragged_nodes(event, d) {
            let newX = event.x;
            let newY = event.y;

            //grid snapping
            if (widgetView.gridSize !== 0) {
                newX = widgetView.gridSize * Math.floor((event.x / widgetView.gridSize) + 0.5);
                newY = widgetView.gridSize * Math.floor((event.y / widgetView.gridSize) + 0.5);
            }

            //force layout
            if (widgetView.forceDirected) {
                event.subject.fx = newX;
                event.subject.fy = newY;
                return
            }

            const nodeId = this.id
            const line = d3.line()

            //move node
            d3.select(widgetView.svg)
                .selectAll(".node")
                .filter(function (data) {
                    return data.id === nodeId;
                })
                .attr("cx", newX)
                .attr("cy", newY)
                .attr("x", newX - d.nodeWidth / 2)
                .attr("y", newY - d.nodeHeight / 2);

            //move node-label
            d3.select(widgetView.svg)
                .selectAll(".nodeLabel")
                .filter(function (data) {
                    return data.id === nodeId;
                })
                .attr("transform", function () { //<-- use transform it's not a g
                    return "translate(" + newX + "," + newY + ")";
                });

            let labelsToMoveIds = []
            //move attached links
            d3.select(widgetView.svg)
                .selectAll(".line")
                .filter(function (data) {
                    return data.source === nodeId || data.target === nodeId;
                })
                .attr("d", function (d) {
                    if (d.source === nodeId) {
                        d.sx = newX
                        d.sy = newY
                    }
                    if (d.target === nodeId) {
                        d.tx = newX
                        d.ty = newY
                    }

                    if (d.bends.length === 0) {
                        labelsToMoveIds.push(d.id)
                    }

                    //selfloop
                    if (d.source === d.target && d.bends.length === 0) {
                        return widgetView.getPath(d.sx, d.sy, d.tx, d.ty);
                    }

                    let points = [[d.sx, d.sy]].concat(d.bends).concat([[d.tx, d.ty]])
                    return line(points)
                })

            //move link-label
            for (let i = 0; i < labelsToMoveIds.length; i++) {
                d3.select(widgetView.svg)
                    .selectAll(".linkLabel")
                    .filter(function (data) {
                        return data.id === labelsToMoveIds[i];
                    })
                    .attr("transform", function (data) { //<-- use transform it's not a g
                        let labelX = (data.sx + data.tx) / 2
                        let labelY = (data.sy + data.ty) / 2
                        return "translate(" + labelX + "," + labelY + ")";
                    });
            }
        }

        function dragEnded_nodes(event, d) {
            const nodeId = this.id

            //returns stroke to normal for dragged node
            d3.select(widgetView.svg)
                .selectAll(".node")
                .filter(function (data) {
                    return data.id === nodeId;
                })
                .attr("stroke-width", function (data) {
                    return data.strokeWidth
                });

            if (widgetView.forceDirected && !event.active) widgetView.simulation.alphaTarget(0);

            //if node only got clicked and not moved
            if (d.startX === event.x && d.startY === event.y) {
                if (widgetView.forceDirected) {
                    event.subject.fx = null;
                    event.subject.fy = null;
                }

                widgetView.send({
                    "code": "nodeClicked",
                    "id": nodeId,
                    "altKey": event.sourceEvent.altKey,
                    "ctrlKey": event.sourceEvent.ctrlKey
                });
            } else {
                d.x = Math.round(event.x)
                d.y = Math.round(event.y)

                if (widgetView.gridSize !== 0) {
                    d.x = widgetView.gridSize * Math.floor((event.x / widgetView.gridSize) + 0.5);
                    d.y = widgetView.gridSize * Math.floor((event.y / widgetView.gridSize) + 0.5);
                }
                widgetView.send({"code": "nodeMoved", "id": this.id, "x": d.x, "y": d.y});
            }
        }
    },

    rescaleAllText() {
        d3.select(this.svg).selectAll(".nodeLabel").style("font-size", this.adaptLabelFontSize)
    },

    rescaleTextById(nodeId) {
        d3.select(this.svg).selectAll(".nodeLabel").filter(function (d) {
            return d.id === nodeId;
        }).style("font-size", this.adaptLabelFontSize)
    },

    adaptLabelFontSize(d) {
        let xPadding, diameter, labelAvailableWidth, labelWidth;

        xPadding = 2;
        diameter = d.nodeWidth;
        labelAvailableWidth = diameter - xPadding;

        labelWidth = this.getComputedTextLength();

        // There is enough space for the label so leave it as is.
        if (labelWidth <= labelAvailableWidth) {
            return '1em';
        }

        /*
         * The meaning of the ratio between labelAvailableWidth and labelWidth equaling 1 is that
         * the label is taking up exactly its available space.
         * With the result as `1em` the font remains the same.
         *
         * The meaning of the ratio between labelAvailableWidth and labelWidth equaling 0.5 is that
         * the label is taking up twice its available space.
         * With the result as `0.5em` the font will change to half its original size.
         */
        return (labelAvailableWidth / labelWidth - 0.01) + 'em';
    }
});

module.exports = {
    WidgetModel: WidgetModel,
    WidgetView: WidgetView,
};
