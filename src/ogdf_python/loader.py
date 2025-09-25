import os
import platform
import warnings
from pathlib import Path

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
CONFIG = os.getenv("OGDF_PYTHON_MODE", "release")
if CONFIG not in ("release", "debug"):
    warnings.warn(f"Environment variable OGDF_PYTHON_MODE set to '{CONFIG}' instead of 'debug' or 'release'.")


## Search Utils

def get_library_path(name=None):
    if name is None:
        if CONFIG == "release":
            return get_library_path("OGDF") or get_library_path("libOGDF")
        else:
            return get_library_path(f"OGDF-{CONFIG}") or get_library_path(f"libOGDF-{CONFIG}")
    return cppyy.gbl.gSystem.FindDynamicLibrary(cppyy.gbl.CppyyLegacy.TString(name), True)


def get_loaded_library_path(name="OGDF"):
    from pathlib import Path
    return [s for s in cppyy.gbl.gSystem.GetLibraries().split(" ") if name in Path(s).name]


def get_base_include_path(include="ogdf/basic/Graph.h"):
    path = get_include_path(include)
    if path:
        path = path.removesuffix(include)
    return path


def get_include_path(name="ogdf/basic/Graph.h"):
    import ctypes
    s = ctypes.c_char_p()
    if cppyy.gbl.gSystem.IsFileInIncludePath(name, s):
        return s.value.decode()
    else:
        return None


def call_if_exists(func, path):
    if Path(path).is_dir():
        func(str(path))
        return True
    return False


## Setup Search Paths

if "OGDF_INSTALL_DIR" in os.environ:
    INSTALL_DIR = Path(os.getenv("OGDF_INSTALL_DIR")).absolute()
    if call_if_exists(cppyy.add_library_path, INSTALL_DIR / "lib64"):
        call_if_exists(cppyy.add_library_path, INSTALL_DIR / "lib")
    else:
        cppyy.add_library_path(str(INSTALL_DIR / "lib"))
    cppyy.add_include_path(str(INSTALL_DIR / "include"))

if "OGDF_BUILD_DIR" in os.environ:
    BUILD_DIR = Path(os.getenv("OGDF_BUILD_DIR")).absolute()
    cppyy.add_library_path(str(BUILD_DIR))
    call_if_exists(cppyy.add_library_path, BUILD_DIR / "Debug")
    call_if_exists(cppyy.add_library_path, BUILD_DIR / "Release")
    cppyy.add_include_path(str(BUILD_DIR / "include"))
    for line in open(BUILD_DIR / "CMakeCache.txt"):
        line = line.strip()
        if line.startswith("OGDF-PROJECT_SOURCE_DIR"):
            key, _, val = line.partition("=")
            cppyy.add_include_path(str(Path(val) / "include"))

try:
    wheel_inst_dir = importlib_resources.files("ogdf_wheel") / "install"
    if wheel_inst_dir.is_dir():
        cppyy.add_library_path(str(wheel_inst_dir / "lib"))
        cppyy.add_include_path(str(wheel_inst_dir / "include"))
except ImportError:
    pass

## Now do the actual loading

cppyy.cppdef("#undef NDEBUG")
if CONFIG == "release":
    cppyy.cppdef("#define NDEBUG")
cppyy.include("cassert")
cppyy.cppdef("#define OGDF_INSTALL")

try:
    if CONFIG == "release":
        cppyy.load_library("COIN")
        cppyy.load_library("OGDF")
    else:
        cppyy.load_library(f"COIN-{CONFIG}")
        cppyy.load_library(f"OGDF-{CONFIG}")

    config_autogen_h = "ogdf/basic/internal/config_autogen.h"
    if not get_include_path(config_autogen_h):
        # try to find the config-dependent header include path if it isn't correctly configured yet
        config_include = get_include_path(f"ogdf-{CONFIG}/{config_autogen_h}")
        if config_include:
            config_include = config_include.removesuffix(config_autogen_h)
            cppyy.add_include_path(config_include)
    cppyy.include(config_autogen_h)

    cppyy.include("ogdf/basic/internal/config.h")
    cppyy.include("ogdf/basic/Graph.h")
    cppyy.include("ogdf/fileformats/GraphIO.h")
    cppyy.include("ogdf/basic/LayoutStandards.h")
except (RuntimeError, ImportError) as e:
    raise ImportError(
        f"ogdf-python couldn't load OGDF in mode '{CONFIG}'.\n"
        "Please check the above underlying error and check that the below search paths contain "
        "OGDF headers and shared libraries in the correct release/debug configuration.\n"
        "If you haven't installed OGDF globally to your system, "
        "you can use the environment variables OGDF_INSTALL_DIR or OGDF_BUILD_DIR.\n"
        f"The current search path is:\n{cppyy.gbl.gSystem.GetDynamicPath()}\n"
        f"The current include path is:\n{cppyy.gbl.gInterpreter.GetIncludePath()}\n"
    ) from e

if CONFIG == "release":
    if cppyy.gbl.ogdf.debugMode:
        warnings.warn("Attempted to load OGDF release build, but the found library was built in debug mode.")
else:
    if not cppyy.gbl.ogdf.debugMode:
        warnings.warn("Attempted to load OGDF debug build, but the found library was built in release mode.")

## Load re-exports
from cppyy import include as cppinclude, cppdef, cppexec, nullptr
from cppyy.gbl import ogdf

__all__ = ["cppyy", "cppinclude", "cppdef", "cppexec", "nullptr", "ogdf",
           "get_library_path", "get_loaded_library_path", "get_include_path", "get_base_include_path"]
__keep_imports = [cppyy, cppinclude, cppdef, cppexec, nullptr, ogdf]
