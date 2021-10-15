var widgets = require('@jupyter-widgets/base');
var _ = require('lodash');
var d3 = require("d3");
require("./style.css");

// See model.py for the kernel counterpart to this file.


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
var HelloModel = widgets.DOMWidgetModel.extend({
    defaults: _.extend(widgets.DOMWidgetModel.prototype.defaults(), {
        _model_name: 'HelloModel',
        _view_name: 'HelloView',
        _model_module: 'ogdf-python-widget',
        _view_module: 'ogdf-python-widget',
        _model_module_version: '0.1.0',
        _view_module_version: '0.1.0',
        value: 'Hello Test!',
    })
});

// Custom View. Renders the widget model.
var HelloView = widgets.DOMWidgetView.extend({
    initialize: function (parameters) {
        HelloView.__super__.initialize.call(this, parameters);
        this.model.on('msg:custom', this.handle_msg.bind(this));

        this.model.on('change:nodes', this.render, this);
        this.model.on('change:links', this.render, this);
    },

    handle_msg: function (msg) {
        console.log(msg)
    },

    // Defines how the widget gets rendered into the DOM
    render: function () {
        console.log("rendering")

        let nodes = this.model.get('nodes')
        let links = this.model.get('links')

        if (this.el.childNodes.length === 0) {
            let svgId = "G" + Math.random().toString(16).slice(2)

            this.svg = document.createElementNS("http://www.w3.org/2000/svg", "svg")
            this.svg.setAttribute("id", svgId)
            this.svg.setAttribute("width", "960");
            this.svg.setAttribute("height", "540");

            this.el.appendChild(this.svg)
            this.send(svgId)
        }

        if (nodes != null && links != null) {
            this.draw_graph.call(this, nodes, links)
        }
    },

    draw_graph(nodes_data, links_data) {

        let svg = d3.select(this.svg),
            width = +svg.attr("width"),
            height = +svg.attr("height");

        let radius = 15;

        //construct arrow
        svg.append("svg:defs").selectAll("marker")
            .data(["endGA"])
            .enter().append("svg:marker")
            .attr("id", String)
            .attr("viewBox", "0 -5 10 10")
            .attr("refX", 28)
            .attr("refY", 0)
            .attr("markerWidth", 8)
            .attr("markerHeight", 8)
            .attr("orient", "auto")
            .attr("fill", "green")
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
            .attr("marker-end", function (d) {
                if (d.arrow) {
                    return "url(#endGA)";
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
            .attr("fill", "none")
            .attr("stroke", "green")
            .on("click", function (event) {
                console.log("on click " + event.target.__data__.id);
            });

        let nodes = g.append("g")
            .attr("class", "node")
            .selectAll("circle")
            .data(nodes_data)
            .enter()
            .append("circle")
            .attr("cx", function (d) {
                return d.x
            })
            .attr("cy", function (d) {
                return d.y
            })
            .attr("r", radius)
            .attr("fill", "green")
            .attr("id", function (d) {
                return d.id
            })
            .on("click", function (event) {
                console.log("on click " + event.target.__data__.name);
            })
            .on("mouseover", handleMouseOver)
            .on("mouseout", handleMouseOut);

        let text = g.append("g")
            .attr("class", "texts")
            .selectAll("text")
            .data(nodes_data)
            .enter()
            .append("text")
            .attr("text-anchor", "middle")
            .attr("dominant-baseline", "central")
            .attr("fill", "white")
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
                console.log("on click " + event.target.__data__.name);
            });


        //add zoom capabilities
        svg.call(d3.zoom()
            .extent([[0, 0], [width, height]])
            .on("zoom", zoomed));


        // this.el.appendChild(this.svg);


        function zoomed({transform}) {
            g.attr("transform", transform);
        }

        // Create Event Handlers for mouse
        function handleMouseOver(d, i) {  // Add interactivity
            // Use D3 to select element, change color and size
            d3.select(this).attr("fill", "orange").attr("r", radius * 1.5);
        }

        function handleMouseOut(d, i) {
            // Use D3 to select element, change color back to normal
            d3.select(this).attr("fill", "green").attr("r", radius);
        }
    }
});


module.exports = {
    HelloModel: HelloModel,
    HelloView: HelloView
};
