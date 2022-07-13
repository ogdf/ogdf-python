import os
import sys

import cppyy.ll
import importlib_resources
from cppyy import include as cppinclude, cppdef, cppexec, nullptr

cppyy.ll.set_signals_as_exception(True)
cppyy.add_include_path(os.path.dirname(os.path.realpath(__file__)))

if "OGDF_INSTALL_DIR" in os.environ:
    INSTALL_DIR = os.path.expanduser(os.getenv("OGDF_INSTALL_DIR"))
    cppyy.add_include_path(os.path.join(INSTALL_DIR, "include"))
    cppyy.add_library_path(os.path.join(INSTALL_DIR, "lib"))
if "OGDF_BUILD_DIR" in os.environ:
    BUILD_DIR = os.path.expanduser(os.getenv("OGDF_BUILD_DIR"))
    cppyy.add_include_path(os.path.join(BUILD_DIR, "include"))
    cppyy.add_include_path(os.path.join(BUILD_DIR, "..", "include"))
    cppyy.add_library_path(BUILD_DIR)
try:
    wheel_inst_dir = importlib_resources.files("ogdf_wheel") / "install"
    if wheel_inst_dir.is_dir():
        cppyy.add_library_path(str(wheel_inst_dir / "lib"))
        cppyy.add_library_path(str(wheel_inst_dir / "bin"))
        cppyy.add_include_path(str(wheel_inst_dir / "include"))
except ImportError:
    pass

cppyy.cppdef("#undef NDEBUG")
try:
    cppyy.include("ogdf/basic/internal/config_autogen.h")
    cppyy.include("ogdf/basic/internal/config.h")
    cppyy.include("ogdf/basic/Graph.h")
    cppyy.include("ogdf/cluster/ClusterGraphObserver.h")  # otherwise only pre-declared
    cppyy.include("ogdf/fileformats/GraphIO.h")

    cppyy.load_library("OGDF")
except:
    print(
        "ogdf-python couldn't load OGDF. "
        "If you haven't installed OGDF globally to your system, "
        "please set environment variables OGDF_INSTALL_DIR or OGDF_BUILD_DIR. "
        "The current search path is:\n%s\n"
        "The current include path is:\n%s" %
        (cppyy.gbl.gSystem.GetDynamicPath(), cppyy.gbl.gInterpreter.GetIncludePath()),
        file=sys.stderr)
    raise

import ogdf_python.doxygen
import ogdf_python.pythonize
import ogdf_python.jupyter
from ogdf_python.info import get_ogdf_info
from cppyy.gbl import ogdf

if ogdf.debugMode:
    cppyy.cppdef("#undef NDEBUG")
else:
    cppyy.cppdef("#define NDEBUG")
cppyy.include("cassert")

try:
    from ogdf_python_widget import _auto_enable
except ImportError:
    pass
else:
    _auto_enable()

__version__ = "0.1.5-dev"
__all__ = ["ogdf", "cppinclude", "cppdef", "cppexec", "nullptr", "__version__", "get_ogdf_info"]
__keep_imports = [cppyy,
                  ogdf_python.doxygen,
                  ogdf_python.pythonize,
                  ogdf_python.jupyter,
                  ogdf, cppinclude, cppdef, cppexec, nullptr]
