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
        _model_module : 'ogdf-python',
        _view_module : 'ogdf-python',
        _model_module_version : '0.1.0',
        _view_module_version : '0.1.0',
        value : 'Hello Test!',
        value2 : 'Hello World!'
    })
});


// Custom View. Renders the widget model.
var HelloView = widgets.DOMWidgetView.extend({
    // Defines how the widget gets rendered into the DOM
    render: function() {
        this.mainDiv = document.createElement("div");
        this.mainDiv.setAttribute("class", "main-div");

        this.subDiv = document.createElement("div");
        this.subDiv.setAttribute("class", "sub-div");


        this.heading = document.createElement("h3");
        this.heading.textContent = 'Überschrift';

        this.mainDiv.appendChild(this.heading);
        this.mainDiv.appendChild(this.subDiv);
        this.el.appendChild(this.mainDiv);

        this.value_changed();
        // // Observe changes in the value traitlet in Python, and define
        // // a custom callback.
        this.model.on('change:value', this.value_changed, this);
        this.model.on('change:value2', this.value_changed, this);
    },

    value_changed: function() {
        this.subDiv.textContent = this.model.get('value') + ' : ' + this.model.get('value2');
    },
});


module.exports = {
    HelloModel: HelloModel,
    HelloView: HelloView
};
