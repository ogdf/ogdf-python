ogdf-python-widget
===============================

A Custom Jupyter Widget Library

Installation
------------

To install use pip:

    $ pip install ogdf_python_widget

For a development installation (requires [Node.js](https://nodejs.org) and [Yarn version 1](https://classic.yarnpkg.com/)),

    $ git clone https://github.com/ogdf/ogdf-python-widget.git
    $ cd ogdf-python-widget
    $ pip install -e .
    $ jupyter nbextension install --py --symlink --overwrite --sys-prefix ogdf_python_widget
    $ jupyter nbextension enable --py --sys-prefix ogdf_python_widget

When actively developing your extension for JupyterLab, run the command:

    $ jupyter labextension develop --overwrite ogdf_python_widget

Then you need to rebuild the JS when you make a code change:

    $ cd js
    $ yarn run build

You then need to refresh the JupyterLab page when your javascript changes.
