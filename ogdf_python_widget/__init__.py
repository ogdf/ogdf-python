import os
import warnings

import cppyy.ll
from cppyy import include as cppinclude, cppdef, nullptr

cppyy.ll.set_signals_as_exception(True)
cppyy.add_include_path(os.path.dirname(os.path.realpath(__file__)))

if "OGDF_INSTALL_DIR" in os.environ:
    INSTALL_DIR = os.path.expanduser(os.getenv("OGDF_INSTALL_DIR"))
    cppyy.add_include_path(os.path.join(INSTALL_DIR, "include"))
    cppyy.add_library_path(os.path.join(INSTALL_DIR, "lib"))
elif "OGDF_BUILD_DIR" in os.environ:
    BUILD_DIR = os.path.expanduser(os.getenv("OGDF_BUILD_DIR"))
    cppyy.add_include_path(os.path.join(BUILD_DIR, "include"))
    cppyy.add_include_path(os.path.join(os.path.dirname(BUILD_DIR), "include"))
    cppyy.add_library_path(BUILD_DIR)
else:
    warnings.warn("ogdf-python couldn't find OGDF. "
                  "Please set environment variables OGDF_INSTALL_DIR or OGDF_BUILD_DIR.")

cppyy.cppdef("#undef NDEBUG")
cppyy.include("ogdf/basic/internal/config_autogen.h")
cppyy.include("ogdf/basic/internal/config.h")
cppyy.include("ogdf/basic/Graph.h")
cppyy.include("ogdf/fileformats/GraphIO.h")

cppyy.load_library("libOGDF.so")

import ogdf_python_widget.pythonize
import ogdf_python_widget.doxygen
import ogdf_python_widget.widget
from cppyy.gbl import ogdf

__all__ = ["ogdf", "cppinclude", "cppdef", "nullptr", "HelloWorld"]
__keep_imports = [cppyy,
                  ogdf_python_widget.doxygen,
                  ogdf_python_widget.pythonize,
                  ogdf_python_widget.widget,
                  ogdf, cppinclude, cppdef, nullptr]

from ogdf_python_widget._version import version_info, __version__


def _jupyter_labextension_paths():
    """Called by Jupyter Lab Server to detect if it is a valid labextension and
    to install the widget

    Returns
    =======
    src: Source directory name to copy files from. Webpack outputs generated files
        into this directory and Jupyter Lab copies from this directory during
        widget installation
    dest: Destination directory name to install widget files to. Jupyter Lab copies
        from `src` directory into <jupyter path>/labextensions/<dest> directory
        during widget installation
    """
    return [{
        'src': 'labextension',
        'dest': 'ogdf-python-widget',
    }]


def _jupyter_nbextension_paths():
    """Called by Jupyter Notebook Server to detect if it is a valid nbextension and
    to install the widget

    Returns
    =======
    section: The section of the Jupyter Notebook Server to change.
        Must be 'notebook' for widget extensions
    src: Source directory name to copy files from. Webpack outputs generated files
        into this directory and Jupyter Notebook copies from this directory during
        widget installation
    dest: Destination directory name to install widget files to. Jupyter Notebook copies
        from `src` directory into <jupyter path>/nbextensions/<dest> directory
        during widget installation
    require: Path to importable AMD Javascript module inside the
        <jupyter path>/nbextensions/<dest> directory
    """
    return [{
        'section': 'notebook',
        'src': 'nbextension',
        'dest': 'ogdf-python-widget',
        'require': 'ogdf-python-widget/extension'
    }]
