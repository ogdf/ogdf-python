(self["webpackChunkogdf_python"] = self["webpackChunkogdf_python"] || []).push([["lib_index_js"],{

/***/ "./lib/example.js":
/*!************************!*\
  !*** ./lib/example.js ***!
  \************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var widgets = __webpack_require__(/*! @jupyter-widgets/base */ "webpack/sharing/consume/default/@jupyter-widgets/base");
var _ = __webpack_require__(/*! lodash */ "webpack/sharing/consume/default/lodash/lodash");
__webpack_require__(/*! ./style.css */ "./lib/style.css");

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


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

// Export widget models and views, and the npm package version number.
module.exports = __webpack_require__(/*! ./example.js */ "./lib/example.js");
module.exports.version = __webpack_require__(/*! ../package.json */ "./package.json").version;


/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./lib/style.css":
/*!*************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./lib/style.css ***!
  \*************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/cssWithMappingToString.js */ "./node_modules/css-loader/dist/runtime/cssWithMappingToString.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
// Imports


var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0___default()));
// Module
___CSS_LOADER_EXPORT___.push([module.id, ".main-div {\n    border: 1px solid #BACACA;\n    background : #D3D3D3;\n    margin-left: auto;\n    margin-right: auto;\n    display: block;\n}\n\n.sub-div {\n    border: 1px solid #BACACA;\n    background : #76ade5;\n    margin-left: auto;\n    margin-right: auto;\n    display: block;\n}", "",{"version":3,"sources":["webpack://./lib/style.css"],"names":[],"mappings":"AAAA;IACI,yBAAyB;IACzB,oBAAoB;IACpB,iBAAiB;IACjB,kBAAkB;IAClB,cAAc;AAClB;;AAEA;IACI,yBAAyB;IACzB,oBAAoB;IACpB,iBAAiB;IACjB,kBAAkB;IAClB,cAAc;AAClB","sourcesContent":[".main-div {\n    border: 1px solid #BACACA;\n    background : #D3D3D3;\n    margin-left: auto;\n    margin-right: auto;\n    display: block;\n}\n\n.sub-div {\n    border: 1px solid #BACACA;\n    background : #76ade5;\n    margin-left: auto;\n    margin-right: auto;\n    display: block;\n}"],"sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./lib/style.css":
/*!***********************!*\
  !*** ./lib/style.css ***!
  \***********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js */ "./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_cjs_js_style_css__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! !!../node_modules/css-loader/dist/cjs.js!./style.css */ "./node_modules/css-loader/dist/cjs.js!./lib/style.css");

            

var options = {};

options.insert = "head";
options.singleton = false;

var update = _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default()(_node_modules_css_loader_dist_cjs_js_style_css__WEBPACK_IMPORTED_MODULE_1__.default, options);



/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (_node_modules_css_loader_dist_cjs_js_style_css__WEBPACK_IMPORTED_MODULE_1__.default.locals || {});

/***/ }),

/***/ "./package.json":
/*!**********************!*\
  !*** ./package.json ***!
  \**********************/
/***/ ((module) => {

"use strict";
module.exports = JSON.parse('{"name":"ogdf-python","version":"0.1.0","description":"A Custom Jupyter Widget Library","author":"Andreas Strobl","main":"lib/index.js","repository":{"type":"git","url":"https://github.com//ogdf-python.git"},"keywords":["jupyter","widgets","ipython","ipywidgets","jupyterlab-extension"],"files":["lib/**/*.js","dist/*.js"],"scripts":{"clean":"rimraf dist/ && rimraf ../ogdf_python/labextension/ && rimraf ../ogdf_python/nbextension","prepublish":"yarn run clean && yarn run build:prod","build":"webpack --mode=development && yarn run build:labextension:dev","build:prod":"webpack --mode=production && yarn run build:labextension","build:labextension":"jupyter labextension build .","build:labextension:dev":"jupyter labextension build --development True .","watch":"webpack --watch --mode=development","test":"echo \\"Error: no test specified\\" && exit 1"},"devDependencies":{"@jupyterlab/builder":"^3.0.0","webpack":"^5","rimraf":"^2.6.1"},"dependencies":{"@jupyter-widgets/base":"^1.1 || ^2 || ^3 || ^4","lodash":"^4.17.4"},"jupyterlab":{"extension":"lib/labplugin","outputDir":"../ogdf_python/labextension","sharedPackages":{"@jupyter-widgets/base":{"bundled":false,"singleton":true}}}}');

/***/ })

}]);
//# sourceMappingURL=lib_index_js.80a136b0305b5beea5d2.js.map