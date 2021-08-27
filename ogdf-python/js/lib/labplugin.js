var plugin = require('./index');
var base = require('@jupyter-widgets/base');

module.exports = {
  id: 'ogdf-python:plugin',
  requires: [base.IJupyterWidgetRegistry],
  activate: function(app, widgets) {
      widgets.registerWidget({
          name: 'ogdf-python',
          version: plugin.version,
          exports: plugin
      });
  },
  autoStart: true
};

