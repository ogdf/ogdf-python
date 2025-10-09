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
IS_DEBUG = CONFIG.lower() == "debug"
CONFIG_RD = "debug" if IS_DEBUG else "release"


## Search Utils

def get_library_path(name=None):
    if name is None:
        if IS_DEBUG:
            return get_library_path("OGDF-debug") or get_library_path("libOGDF-debug")
        else:
            return get_library_path("OGDF") or get_library_path("libOGDF")
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


def get_macro(m):
    var_name = "var_%s" % m
    if not hasattr(cppyy.gbl, "get_macro") or not hasattr(cppyy.gbl.get_macro, var_name):
        cppyy.cppdef("""
#define STR(str) #str
#define STRING(str) STR(str)
namespace get_macro {{
#ifdef {m}  
    std::string var_{m} = STRING({m});
#endif
}};
""".format(m=m))
    val = getattr(cppyy.gbl.get_macro, var_name, None)
    if val is not None:
        val = val.decode("ascii")
    return val


## Setup Search Paths

if "OGDF_INSTALL_DIR" in os.environ:
    INSTALL_DIR = Path(os.getenv("OGDF_INSTALL_DIR")).absolute()
    if call_if_exists(cppyy.add_library_path, INSTALL_DIR / "lib64"):
        call_if_exists(cppyy.add_library_path, INSTALL_DIR / "lib")
    else:
        cppyy.add_library_path(str(INSTALL_DIR / "lib"))
    cppyy.add_include_path(str(INSTALL_DIR / "include"))

if "OGDF_BUILD_DIR" in os.environ:
    BUILD_TARGETS = Path(os.getenv("OGDF_BUILD_DIR")) / "OgdfTargets.cmake"
    if BUILD_TARGETS.is_file():
        values = {}
        active = False
        for line in BUILD_TARGETS.open():
            line = line.strip()
            if active:
                if line == ")":
                    active = False
                else:
                    pref, _, suff = line.partition(" ")
                    values[pref] = suff.strip('"')
            elif line == "set_target_properties(OGDF PROPERTIES":
                active = True

        includes =values.get("INTERFACE_INCLUDE_DIRECTORIES",None)
        if includes:
            includes = includes.replace(r"\$<IF:\$<CONFIG:Debug>,debug,release>", CONFIG_RD)
            for s in includes.split(";"):
                cppyy.add_include_path(s)
        else:
            warnings.warn("$OGDF_BUILD_DIR/OgdfTargets.cmake does not specify INTERFACE_INCLUDE_DIRECTORIES for OGDF.")
        location = values.get("IMPORTED_LOCATION_" + CONFIG.upper(), None)
        if location:
            cppyy.add_library_path(str(Path(location).parent))
        else:
            warnings.warn("$OGDF_BUILD_DIR/OgdfTargets.cmake does not specify IMPORTED_LOCATION_${OGDF_PYTHON_MODE}"
                          f" for mode {CONFIG.upper()}.")
    else:
        warnings.warn("Environment variable OGDF_BUILD_DIR set, but $OGDF_BUILD_DIR/OgdfTargets.cmake not found.")

try:
    wheel_inst_dir = importlib_resources.files("ogdf_wheel") / "install"
    if wheel_inst_dir.is_dir():
        cppyy.add_library_path(str(wheel_inst_dir / "lib"))
        cppyy.add_include_path(str(wheel_inst_dir / "include"))
except ImportError:
    pass

## Now do the actual loading

cppyy.cppdef("#undef NDEBUG")
if not IS_DEBUG:
    cppyy.cppdef("#define NDEBUG")
cppyy.include("cassert")
cppyy.cppdef("#define OGDF_INSTALL")

try:
    if IS_DEBUG:
        cppyy.load_library("COIN-debug")
        cppyy.load_library("OGDF-debug")
    else:
        cppyy.load_library("COIN")
        cppyy.load_library("OGDF")

    config_autogen_h = "ogdf/basic/internal/config_autogen.h"
    if not get_include_path(config_autogen_h):
        # try to find the config-dependent header include path if it isn't correctly configured yet
        config_include = get_include_path(f"ogdf-{CONFIG_RD}/{config_autogen_h}")
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

if IS_DEBUG:
    if not cppyy.gbl.ogdf.debugMode:
        warnings.warn("Attempted to load OGDF debug build, but the found library was built in release mode.")
    if get_macro("OGDF_DEBUG") is None:
        warnings.warn("Attempted to load OGDF debug build, but the found headers are for release mode.")
else:
    if cppyy.gbl.ogdf.debugMode:
        warnings.warn("Attempted to load OGDF release build, but the found library was built in debug mode.")
    if get_macro("OGDF_DEBUG") is not None:
        warnings.warn("Attempted to load OGDF release build, but the found headers are for debug mode.")

## Load re-exports
from cppyy import include as cppinclude, cppdef, cppexec, nullptr
from cppyy.gbl import ogdf

__all__ = ["cppyy", "cppinclude", "cppdef", "cppexec", "nullptr", "ogdf",
           "get_library_path", "get_loaded_library_path", "get_include_path", "get_base_include_path",
           "get_macro"]
__keep_imports = [cppyy, cppinclude, cppdef, cppexec, nullptr, ogdf]
