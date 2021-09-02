var widgets = require('@jupyter-widgets/base');
var _ = require('lodash');
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

// When serialiazing the entire widget state for embedding, only values that
// differ from the defaults will be specified.
var HelloModel = widgets.DOMWidgetModel.extend({
    defaults: _.extend(widgets.DOMWidgetModel.prototype.defaults(), {
        _model_name : 'HelloModel',
        _view_name : 'HelloView',
        _model_module : 'ogdf-python-widget',
        _view_module : 'ogdf-python-widget',
        _model_module_version : '0.1.0',
        _view_module_version : '0.1.0',
        value: 'Hello Test!',
        value2: 'Hello World!'
    })
});


// Custom View. Renders the widget model.
var HelloView = widgets.DOMWidgetView.extend({
    // Defines how the widget gets rendered into the DOM
    render: function () {
        this.mainDiv = document.createElement("div");
        this.mainDiv.setAttribute("class", "main-div");

        this.subDiv = document.createElement("div");
        this.subDiv.setAttribute("class", "sub-div");

        this.sketch = document.createElement("div");


        this.heading = document.createElement("h3");
        this.heading.textContent = 'Überschrift';

        this.mainDiv.appendChild(this.heading);
        this.mainDiv.appendChild(this.subDiv);

        this.canvas = document.createElement("canvas");
        this.context = this.canvas.getContext('2d');
        this.context.canvas.width = 2000
        this.context.canvas.height = 1000

        this.sketch.appendChild(this.canvas);
        this.mainDiv.appendChild(this.sketch);
        this.el.appendChild(this.mainDiv);

        this.value_changed();
        this.draw_graph();

        this.model.on('change:value', this.value_changed, this);
        this.model.on('change:value2', this.value_changed, this);
        this.model.on('change:nodes', this.draw_graph, this);
        this.model.on('change:edges', this.draw_graph, this);
    },

    value_changed: function () {
        this.subDiv.textContent = this.model.get('value') + ' : ' + this.model.get('value2');
    },

    draw_graph: function () {
        console.log('drawing graph')
        const edges = this.model.get('edges');
        for (let i = 0; i < edges.length; i++) {
            const edge = edges[i];
            this.draw_line(edge[0], edge[1], edge[2], edge[3], this.context)
        }

        const nodes = this.model.get('nodes');
        for (let i = 0; i < nodes.length; i++) {
            const node = nodes[i];
            this.draw_circle(node[0], node[1], 20, this.context)
            this.draw_text(node[0], node[1], node[2], this.context)
        }
        console.log(nodes.length)
    },

    draw_circle: function (centerX, centerY, radius, context) {
        context.beginPath();
        context.arc(centerX, centerY, radius, 0, 2 * Math.PI, false);
        context.fillStyle = 'green';
        context.fill();
        context.lineWidth = 1;
        context.strokeStyle = '#003300';
        context.stroke();
    },

    draw_line: function (sourceX, sourceY, targetX, targetY, context) {
        context.strokeStyle = 'green';
        context.lineWidth = 2;
        context.beginPath();
        context.moveTo(sourceX, sourceY);
        context.lineTo(targetX, targetY);
        context.stroke();
    },

    draw_text: function (x, y, text, context) {
        context.fillStyle = 'black';
        context.font = "20px Arial";
        context.textAlign = "center";
        context.fillText(text, x, y);
    },
});


module.exports = {
    HelloModel: HelloModel,
    HelloView: HelloView
};
