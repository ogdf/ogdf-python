var widgets = require('@jupyter-widgets/base');
var _ = require('lodash');
var d3 = require("d3");
require("./style.css");

// See example.py for the kernel counterpart to this file.


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
        value2: 'Hello World!',
        refresh: false,


    })

});

// Custom View. Renders the widget model.
var HelloView = widgets.DOMWidgetView.extend({
    // Defines how the widget gets rendered into the DOM
    render: function () {
        this.svg = document.createElementNS("http://www.w3.org/2000/svg", "svg")

        this.svg.setAttribute("width", "960");
        this.svg.setAttribute("height", "540");

        var svg = d3.select(this.svg),
            width = +svg.attr("width"),
            height = +svg.attr("height");

        var radius = 15;

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

        var nodes_data = [{"id": "0", "name": "0", "x": 250, "y": 40}, {
            "id": "1",
            "name": "1",
            "x": 220,
            "y": 90
        }, {"id": "2", "name": "2", "x": 200, "y": 575}, {"id": "3", "name": "3", "x": 150, "y": 732}, {
            "id": "7",
            "name": "7",
            "x": 160,
            "y": 515
        }, {"id": "8", "name": "8", "x": 240, "y": 465}, {"id": "9", "name": "9", "x": 40, "y": 575}, {
            "id": "10",
            "name": "10",
            "x": 150,
            "y": 782
        }, {"id": "11", "name": "11", "x": 220, "y": 362}, {"id": "12", "name": "12", "x": 380, "y": 262}, {
            "id": "13",
            "name": "13",
            "x": 240,
            "y": 942
        }, {"id": "14", "name": "14", "x": 80, "y": 782}, {"id": "15", "name": "15", "x": 290, "y": 262}, {
            "id": "16",
            "name": "16",
            "x": 180,
            "y": 140
        }, {"id": "17", "name": "17", "x": 335, "y": 212}, {"id": "18", "name": "18", "x": 260, "y": 312}, {
            "id": "19",
            "name": "19",
            "x": 260,
            "y": 415
        }, {"id": "20", "name": "20", "x": 280, "y": 625}, {"id": "21", "name": "21", "x": 240, "y": 855}, {
            "id": "22",
            "name": "22",
            "x": 180,
            "y": 625
        }]
        var links_data = [{"source": "16", "target": "0"}, {
            "id": "0_1",
            "sx": 250,
            "sy": 40,
            "tx": 220,
            "ty": 90,
            "arrow": true
        }, {"id": "12_20", "sx": 380, "sy": 262, "tx": 360, "ty": 312}, {
            "id": "12_20",
            "sx": 360,
            "sy": 312,
            "tx": 360,
            "ty": 575
        }, {"id": "12_20", "sx": 360, "sy": 575, "tx": 280, "ty": 625, "arrow": true}, {
            "id": "12_21",
            "sx": 380,
            "sy": 262,
            "tx": 400,
            "ty": 312
        }, {"id": "12_21", "sx": 400, "sy": 312, "tx": 400, "ty": 782}, {
            "id": "12_21",
            "sx": 400,
            "sy": 782,
            "tx": 240,
            "ty": 855,
            "arrow": true
        }, {"id": "11_8", "sx": 220, "sy": 362, "tx": 220, "ty": 415}, {
            "id": "11_8",
            "sx": 220,
            "sy": 415,
            "tx": 240,
            "ty": 465,
            "arrow": true
        }, {"id": "16_9", "sx": 180, "sy": 140, "tx": 40, "ty": 212}, {
            "id": "16_9",
            "sx": 40,
            "sy": 212,
            "tx": 40,
            "ty": 515
        }, {"id": "16_9", "sx": 40, "sy": 515, "tx": 40, "ty": 575, "arrow": true}, {
            "id": "2_22",
            "sx": 200,
            "sy": 575,
            "tx": 180,
            "ty": 625,
            "arrow": true
        }, {"id": "14_7", "sx": 80, "sy": 782, "tx": 80, "ty": 732}, {
            "id": "14_7",
            "sx": 80,
            "sy": 732,
            "tx": 80,
            "ty": 575
        }, {"id": "14_7", "sx": 80, "sy": 575, "tx": 160, "ty": 515, "arrow": true}, {
            "id": "7_2",
            "sx": 160,
            "sy": 515,
            "tx": 200,
            "ty": 575,
            "arrow": true
        }, {"id": "2_20", "sx": 200, "sy": 575, "tx": 280, "ty": 625, "arrow": true}, {
            "id": "7_9",
            "sx": 160,
            "sy": 515,
            "tx": 40,
            "ty": 575,
            "arrow": true
        }, {"id": "9_14", "sx": 40, "sy": 575, "tx": 40, "ty": 625}, {
            "id": "9_14",
            "sx": 40,
            "sy": 625,
            "tx": 40,
            "ty": 732
        }, {"id": "9_14", "sx": 40, "sy": 732, "tx": 80, "ty": 782, "arrow": true}, {
            "id": "3_10",
            "sx": 150,
            "sy": 732,
            "tx": 150,
            "ty": 782,
            "arrow": true
        }, {"id": "16_11", "sx": 180, "sy": 140, "tx": 200, "ty": 212}, {
            "id": "16_11",
            "sx": 200,
            "sy": 212,
            "tx": 200,
            "ty": 312
        }, {"id": "16_11", "sx": 200, "sy": 312, "tx": 220, "ty": 362, "arrow": true}, {
            "id": "19_18",
            "sx": 260,
            "sy": 415,
            "tx": 280,
            "ty": 362
        }, {"id": "19_18", "sx": 280, "sy": 362, "tx": 260, "ty": 312, "arrow": true}, {
            "id": "17_12",
            "sx": 335,
            "sy": 212,
            "tx": 380,
            "ty": 262,
            "arrow": true
        }, {"id": "10_13", "sx": 150, "sy": 782, "tx": 150, "ty": 855}, {
            "id": "10_13",
            "sx": 150,
            "sy": 855,
            "tx": 240,
            "ty": 942,
            "arrow": true
        }, {"id": "22_3", "sx": 180, "sy": 625, "tx": 150, "ty": 732, "arrow": true}, {
            "id": "3_14",
            "sx": 150,
            "sy": 732,
            "tx": 80,
            "ty": 782,
            "arrow": true
        }, {"id": "0_15", "sx": 250, "sy": 40, "tx": 290, "ty": 90}, {
            "id": "0_15",
            "sx": 290,
            "sy": 90,
            "tx": 290,
            "ty": 212
        }, {"id": "0_15", "sx": 290, "sy": 212, "tx": 290, "ty": 262, "arrow": true}, {
            "id": "18_1",
            "sx": 260,
            "sy": 312,
            "tx": 240,
            "ty": 262
        }, {"id": "18_1", "sx": 240, "sy": 262, "tx": 240, "ty": 140}, {
            "id": "18_1",
            "sx": 240,
            "sy": 140,
            "tx": 220,
            "ty": 90,
            "arrow": true
        }, {"id": "1_16", "sx": 220, "sy": 90, "tx": 180, "ty": 140, "arrow": true}, {
            "id": "0_17",
            "sx": 250,
            "sy": 40,
            "tx": 335,
            "ty": 90
        }, {"id": "0_17", "sx": 335, "sy": 90, "tx": 335, "ty": 140}, {
            "id": "0_17",
            "sx": 335,
            "sy": 140,
            "tx": 335,
            "ty": 212,
            "arrow": true
        }, {"id": "17_15", "sx": 335, "sy": 212, "tx": 290, "ty": 262, "arrow": true}, {
            "id": "15_18",
            "sx": 290,
            "sy": 262,
            "tx": 260,
            "ty": 312,
            "arrow": true
        }, {"id": "11_19", "sx": 220, "sy": 362, "tx": 260, "ty": 415, "arrow": true}, {
            "id": "19_8",
            "sx": 260,
            "sy": 415,
            "tx": 240,
            "ty": 465,
            "arrow": true
        }, {"id": "8_20", "sx": 240, "sy": 465, "tx": 240, "ty": 515}, {
            "id": "8_20",
            "sx": 240,
            "sy": 515,
            "tx": 240,
            "ty": 575
        }, {"id": "8_20", "sx": 240, "sy": 575, "tx": 280, "ty": 625, "arrow": true}, {
            "id": "10_21",
            "sx": 150,
            "sy": 782,
            "tx": 240,
            "ty": 855,
            "arrow": true
        }, {"id": "21_13", "sx": 240, "sy": 855, "tx": 240, "ty": 942, "arrow": true}, {
            "id": "13_22",
            "sx": 240,
            "sy": 942,
            "tx": 440,
            "ty": 855
        }, {"id": "13_22", "sx": 440, "sy": 855, "tx": 440, "ty": 732}, {
            "id": "13_22",
            "sx": 440,
            "sy": 732,
            "tx": 180,
            "ty": 625,
            "arrow": true
        }, {"id": "11_7", "sx": 220, "sy": 362, "tx": 120, "ty": 415}, {
            "id": "11_7",
            "sx": 120,
            "sy": 415,
            "tx": 120,
            "ty": 465
        }, {"id": "11_7", "sx": 120, "sy": 465, "tx": 160, "ty": 515, "arrow": true}, {
            "id": "16_17",
            "sx": 180,
            "sy": 140,
            "tx": 335,
            "ty": 212,
            "arrow": true
        }, {"id": "22_7", "sx": 180, "sy": 625, "tx": 160, "ty": 575}, {
            "id": "22_7",
            "sx": 160,
            "sy": 575,
            "tx": 160,
            "ty": 515,
            "arrow": true
        }, {"id": "8_7", "sx": 240, "sy": 465, "tx": 160, "ty": 515, "arrow": true}, {
            "id": "3_7",
            "sx": 150,
            "sy": 732,
            "tx": 120,
            "ty": 625
        }, {"id": "3_7", "sx": 120, "sy": 625, "tx": 120, "ty": 575}, {
            "id": "3_7",
            "sx": 120,
            "sy": 575,
            "tx": 160,
            "ty": 515,
            "arrow": true
        }, {"id": "21_22", "sx": 240, "sy": 855, "tx": 240, "ty": 782}, {
            "id": "21_22",
            "sx": 240,
            "sy": 782,
            "tx": 240,
            "ty": 732
        }, {"id": "21_22", "sx": 240, "sy": 732, "tx": 180, "ty": 625, "arrow": true}, {
            "id": "7_16",
            "sx": 160,
            "sy": 515,
            "tx": 160,
            "ty": 465
        }, {"id": "7_16", "sx": 160, "sy": 465, "tx": 160, "ty": 212}, {
            "id": "7_16",
            "sx": 160,
            "sy": 212,
            "tx": 180,
            "ty": 140,
            "arrow": true
        }, {"id": "18_11", "sx": 260, "sy": 312, "tx": 220, "ty": 362, "arrow": true}, {
            "id": "20_15",
            "sx": 280,
            "sy": 625,
            "tx": 320,
            "ty": 575
        }, {"id": "20_15", "sx": 320, "sy": 575, "tx": 320, "ty": 312}, {
            "id": "20_15",
            "sx": 320,
            "sy": 312,
            "tx": 290,
            "ty": 262,
            "arrow": true
        }, {"id": "16_0", "sx": 180, "sy": 140, "tx": 180, "ty": 90}, {
            "id": "16_0",
            "sx": 180,
            "sy": 90,
            "tx": 250,
            "ty": 40,
            "arrow": true
        }]

        //add encompassing group for the zoom
        var g = svg.append("g").attr("class", "everything");

        var links = g.append("g")
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

        var nodes = g.append("g")
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
            .on("click", function (event) {
                console.log("on click " + event.target.__data__.name);
            });

        var text = g.append("g")
            .attr("class", "texts")
            .selectAll("text")
            .data(nodes_data)
            .enter()
            .append("text")
            .attr("text-anchor", "middle")
            .attr("dominant-baseline", "central")
            .attr("fill", "white")
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

        function zoomed({transform}) {
            g.attr("transform", transform);
        }

        this.el.appendChild(this.svg);

        // this.model.on('change:value', this.value_changed, this);
    },
});


module.exports = {
    HelloModel: HelloModel,
    HelloView: HelloView
};
