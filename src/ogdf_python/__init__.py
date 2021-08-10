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

import ogdf_python.doxygen
import ogdf_python.pythonize
from cppyy.gbl import ogdf

__all__ = ["ogdf", "cppinclude", "cppdef", "nullptr"]
__keep_imports = [cppyy,
                  ogdf_python.doxygen,
                  ogdf_python.pythonize,
                  ogdf, cppinclude, cppdef, nullptr]
