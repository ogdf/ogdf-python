.. |binder| image:: https://mybinder.org/badge_logo.svg
 :target: https://mybinder.org/v2/gh/N-Coder/ogdf-python/HEAD?labpath=docs%2Fexamples%2Fsugiyama-simple.ipynb
.. |(TM)| unicode:: U+2122

ogdf-python 0.2.1: Automagic Python Bindings for the Open Graph Drawing Framework |binder|
==============================================================================================

``ogdf-python`` uses the `black magic <http://www.camillescott.org/2019/04/11/cmake-cppyy/>`_
of the awesome `cppyy <https://bitbucket.org/wlav/cppyy/src/master/>`_ library to automagically generate python bindings
for the C++ `Open Graph Drawing Framework (OGDF) <https://ogdf.uos.de/>`_.
It is available for Python>=3.6 and is Apache2 licensed.
There are no binding definitions files, no stuff that needs extra compiling, it just works\ |(TM)|, believe me.
Templates, namespaces, cross-language callbacks and inheritance, pythonic iterators and generators, it's all there.
If you want to learn more about the magic behind the curtains, read `this article <http://www.camillescott.org/2019/04/11/cmake-cppyy/>`_.

Useful Links
------------
`Original repository <https://github.com/N-Coder/ogdf-python>`_ (GitHub) -
`Bugtracker and issues <https://github.com/N-Coder/ogdf-python>`_ (GitHub) -
`PyPi package <https://pypi.python.org/pypi/ogdf-python>`_ (PyPi ``ogdf-python``) -
`Try it out! <https://mybinder.org/v2/gh/N-Coder/ogdf-python/HEAD?labpath=docs%2Fexamples%2Fsugiyama-simple.ipynb>`_ (mybinder.org).

`Official OGDF website <https://ogdf.uos.de/>`_ (ogdf.net) -
`Public OGDF repository <https://github.com/ogdf/ogdf>`_ (GitHub) -
`OGDF Documentation <https://ogdf.github.io/docs/ogdf/>`_ (GitHub / Doxygen) -
`cppyy Documentation <https://cppyy.readthedocs.io>`_ (Read The Docs).

..
    `Documentation <https://ogdf-python.readthedocs.io>`_ (Read The Docs)
    `Internal OGDF repository <https://git.tcs.uos.de/ogdf-devs/OGDF>`_ (GitLab)


Quickstart
----------

Click here to start an interactive online Jupyter Notebook with an example OGDF graph where you can try out ``ogdf-python``: |binder|

Simply re-run the code cell to see the graph. You can also find further examples next to that Notebook (i.e. via the folder icon on the left).
To get a similar Jupyter Notebook with a little more compute power running on your local machine, use the following install command and open the link to ``localhost``/``127.0.0.1`` that will be printed in your browser:

.. code-block:: bash

    pip install ogdf-python[quickstart]
    jupyter lab

The optional ``[quickstart]`` pulls in matplotlib and jupyter lab as well as a ready-to-use binary build of the OGDF via `ogdf-wheel <https://github.com/ogdf/ogdf-wheel>`_.
Please not that downloading and installing all dependencies (especially building ``cppyy``) may take a moment.
Alternatively, see the instructions `below <#manual-installation>`_ for installing ``ogdf-python`` without this if you want to use your own local build of the OGDF.

Usage
-----
``ogdf-python`` works very well with Jupyter:

.. code-block:: python

    # %matplotlib widget
    # uncomment the above line if you want the interactive display

    from ogdf_python import *
    cppinclude("ogdf/basic/graph_generators/randomized.h")
    cppinclude("ogdf/layered/SugiyamaLayout.h")

    G = ogdf.Graph()
    ogdf.setSeed(1)
    ogdf.randomPlanarTriconnectedGraph(G, 20, 40)
    GA = ogdf.GraphAttributes(G, ogdf.GraphAttributes.all)

    for n in G.nodes:
        GA.label[n] = "N%s" % n.index()

    SL = ogdf.SugiyamaLayout()
    SL.call(GA)
    GA

.. image:: docs/examples/sugiyama-simple.svg
    :target: docs/examples/sugiyama-simple.ipynb
    :alt: SugiyamaLayouted Graph
    :height: 300 px

Read the `pitfalls section <#pitfalls>`_ and check out `docs/examples/pitfalls.ipynb <docs/examples/pitfalls.ipynb>`_
for the more advanced Sugiyama example from the OGDF docs.
There is also a bigger example in `docs/examples/ogdf-includes.ipynb <docs/examples/ogdf-includes.ipynb>`_.
If anything is unclear, check out the python help ``help(ogdf.Graph)`` and read the corresponding OGDF documentation.

Installation without ogdf-wheel
-------------------------------

Use pip to install the ``ogdf-python`` package locally on your machine.
Please note that building ``cppyy`` from sources may take a while.
Furthermore, you will need a local shared library build (``-DBUILD_SHARED_LIBS=ON``) of the `OGDF <https://ogdf.github.io/doc/ogdf/md_doc_build.html>`_.
If you didn't install the OGDF globally on your system,
either set the ``OGDF_INSTALL_DIR`` to the prefix you configured in ``cmake``,
or set ``OGDF_BUILD_DIR`` to the subdirectory of your copy of the OGDF repo where your
`out-of-source build <https://ogdf.github.io/doc/ogdf/md_doc_build.html#autotoc_md4>`_ lives.

.. code-block:: bash

    $ pip install ogdf-python
    $ OGDF_BUILD_DIR=~/ogdf/build-debug python3

Pitfalls
--------

See also `docs/examples/pitfalls.ipynb <docs/examples/pitfalls.ipynb>`_ for full examples.

OGDF sometimes takes ownership of objects (usually when they are passed as modules),
which may conflict with the automatic cppyy garbage collection.
Set ``__python_owns__ = False`` on those objects to tell cppyy that those objects
don't need to be garbage collected, but will be cleaned up from the C++ side.

.. code-block:: python

    SL = ogdf.SugiyamaLayout()
    ohl = ogdf.OptimalHierarchyLayout()
    ohl.__python_owns__ = False
    SL.setLayout(ohl)

When you overwrite a python variable pointing to a C++ object (and it is the only
python variable pointing to that object), the C++ object will usually be immediately deleted.
This might be a problem if another C++ objects depends on that old object, e.g.
a ``GraphAttributes`` instance depending on a ``Graph`` instance.
Now the other C++ object has a pointer to a deleted and now invalid location,
which will usually cause issues down the road (e.g. when the dependant object is
deleted and wants to deregister from its no longer alive parent).
This overwriting might easily happen if you run a Jupyter cell multiple times or some code in a ``for``-loop.
Please ensure that you always overwrite or delete dependent C++ variables in
the reverse order of their initialization.

.. code-block:: python

    for i in range(5):
        # clean-up all variables
        CGA = CG = G = None # note that order is different from C++, CGA will be deleted first, G last
        # now we can re-use them
        G = ogdf.Graph()
        CG = ogdf.ClusterGraph(G)
        CGA = ogdf.ClusterGraphAttributes(CG, ogdf.ClusterGraphAttributes.all)

        # alternatively manually clean up in the right order
        del CGA
        del CG
        del G

There seems to be memory leak in the Jupyter Lab server which causes it to use large amounts of memory
over time while working with ogdf-python. On Linux, the following command can be used to limit this memory usage:

.. code-block:: bash

    systemd-run --scope -p MemoryMax=5G --user -- jupyter notebook
