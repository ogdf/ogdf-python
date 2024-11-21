import os
import platform

import importlib_resources
import sys

try:
    import cppyy
    import cppyy.ll
except:
    print(
        "\n##########\n"
        "ogdf-python couldn't load cppyy. "
        "This is not an ogdf-python error, but probably a problem with your cppyy installation or python environment. "
        "To use ogdf-python, check that you can `import cppyy` in a freshly-started python interpreter.\n",
        file=sys.stderr
    )
    if platform.system() == "Windows":
        print(
            "Note that ogdf-python is not officially supported on Windows."
            "Instead, you should use ogdf-python within the Windows Subsystem for Linux (WSL)."
            "There, make sure to actually invoke the Linux python(3) binary instead of the Windows python.exe, which"
            "can be checked with `python -VV`.\n",
            file=sys.stderr
        )
    print("##########\n\n", file=sys.stderr)
    raise

cppyy.ll.set_signals_as_exception(True)
cppyy.add_include_path(os.path.dirname(os.path.realpath(__file__)))

if "OGDF_INSTALL_DIR" in os.environ:
    INSTALL_DIR = os.path.expanduser(os.getenv("OGDF_INSTALL_DIR"))
    cppyy.add_include_path(os.path.join(INSTALL_DIR, "include"))
    cppyy.add_library_path(os.path.join(INSTALL_DIR, "lib"))  # TODO windows?
if "OGDF_BUILD_DIR" in os.environ:
    BUILD_DIR = os.path.expanduser(os.getenv("OGDF_BUILD_DIR"))
    cppyy.add_include_path(os.path.join(BUILD_DIR, "include"))
    cppyy.add_include_path(os.path.join(BUILD_DIR, "..", "include"))  # TODO not canonical
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
cppyy.cppdef("#define OGDF_INSTALL")
try:
    cppyy.include("ogdf/basic/internal/config_autogen.h")
    cppyy.include("ogdf/basic/internal/config.h")
    cppyy.include("ogdf/basic/Graph.h")
    cppyy.include("ogdf/cluster/ClusterGraphObserver.h")  # otherwise only pre-declared
    cppyy.include("ogdf/fileformats/GraphIO.h")

    cppyy.load_library("OGDF")
except:
    print(  # TODO check if the issue is really that the file couldn't be found
        "ogdf-python couldn't load OGDF. "
        "If you haven't installed OGDF globally to your system, "
        "please set environment variables OGDF_INSTALL_DIR or OGDF_BUILD_DIR. "
        "The current search path is:\n%s\n"
        "The current include path is:\n%s\n" %
        (cppyy.gbl.gSystem.GetDynamicPath(), cppyy.gbl.gInterpreter.GetIncludePath()),
        file=sys.stderr)
    raise

if cppyy.gbl.ogdf.debugMode:
    cppyy.cppdef("#undef NDEBUG")
else:
    cppyy.cppdef("#define NDEBUG")
cppyy.include("cassert")

# Load re-exports
from cppyy import include as cppinclude, cppdef, cppexec, nullptr
from cppyy.gbl import ogdf

__all__ = ["cppyy", "cppinclude", "cppdef", "cppexec", "nullptr", "ogdf"]
__keep_imports = [cppyy, cppinclude, cppdef, cppexec, nullptr, ogdf]
