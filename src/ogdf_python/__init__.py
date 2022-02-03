import os
import sys

import cppyy.ll
from cppyy import include as cppinclude, cppdef, cppexec, nullptr

cppyy.ll.set_signals_as_exception(True)
cppyy.add_include_path(os.path.dirname(os.path.realpath(__file__)))

if "OGDF_INSTALL_DIR" in os.environ:
    INSTALL_DIR = os.path.expanduser(os.getenv("OGDF_INSTALL_DIR"))
    cppyy.add_include_path(os.path.join(INSTALL_DIR, "include"))
    cppyy.add_library_path(os.path.join(INSTALL_DIR, "lib"))
elif "OGDF_BUILD_DIR" in os.environ:
    BUILD_DIR = os.path.expanduser(os.getenv("OGDF_BUILD_DIR"))
    cppyy.add_include_path(os.path.join(BUILD_DIR, "include"))
    cppyy.add_include_path(os.path.join(BUILD_DIR, "..", "include"))
    cppyy.add_library_path(BUILD_DIR)

cppyy.cppdef("#undef NDEBUG")
try:
    cppyy.include("ogdf/basic/internal/config_autogen.h")
    cppyy.include("ogdf/basic/internal/config.h")
    cppyy.include("ogdf/basic/Graph.h")
    cppyy.include("ogdf/fileformats/GraphIO.h")

    cppyy.load_library("libOGDF")
except:
    print(
        "ogdf-python couldn't load OGDF. "
        "If you haven't installed OGDF globally to your system, "
        "please set environment variables OGDF_INSTALL_DIR or OGDF_BUILD_DIR.",
        file=sys.stderr)
    raise

import ogdf_python.doxygen
import ogdf_python.pythonize
import ogdf_python.jupyter
from cppyy.gbl import ogdf

__version__ = "0.1.3"
__all__ = ["ogdf", "cppinclude", "cppdef", "cppexec", "nullptr", "__version__"]
__keep_imports = [cppyy,
                  ogdf_python.doxygen,
                  ogdf_python.pythonize,
                  ogdf_python.jupyter,
                  ogdf, cppinclude, cppdef, cppexec, nullptr]
