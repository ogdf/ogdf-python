// This file contains the javascript that is run when the notebook is loaded.
// It contains some requirejs configuration and the `load_ipython_extension`
// which is required for any notebook extension.
//
// Some static assets may be required by the custom widget javascript. The base
// url for the notebook is not known at build time and is therefore computed
// dynamically.
__webpack_public_path__ = document.querySelector('body').getAttribute('data-base-url') + 'nbextensions/ogdf-python-widget';


// Configure requirejs
if (window.require) {
    window.require.config({
        map: {
            "*" : {
                "ogdf-python-widget": "nbextensions/ogdf-python-widget/index",
                "d3": "https://d3js.org/d3.v7.min.js?noext"
            }
        }
    });
}

// Export the required load_ipython_extension
module.exports = {
    load_ipython_extension: function() {}
};
