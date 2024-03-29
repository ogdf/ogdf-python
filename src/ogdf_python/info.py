from ogdf_python.loader import *

__all__ = ["get_ogdf_info", "get_macro", "get_library_path", "get_include_path", "get_ogdf_include_path"]


def get_macro(m):
    cppdef("""
#define STR(str) #str
#define STRING(str) STR(str)
namespace get_macro {{
#ifdef {m}  
    std::string var_{m} = STRING({m});
#endif
}};
""".format(m=m))
    val = getattr(cppyy.gbl.get_macro, "var_%s" % m, None)
    if val is not None:
        val = val.decode("ascii")
    return val


def conf_which(n):
    w = "which%s" % n
    cppdef("""
namespace conf_which {{
    std::string {w}() {{
        return ogdf::Configuration::toString(ogdf::Configuration::{w}());
    }}
}};
""".format(w=w))
    return getattr(cppyy.gbl.conf_which, w)().decode("ascii")


def get_library_path(name=None):
    if name is None:
        return get_library_path("OGDF") or get_library_path("libOGDF")
    return cppyy.gbl.gSystem.FindDynamicLibrary(cppyy.gbl.CppyyLegacy.TString(name), True)


def get_ogdf_include_path():
    include = "ogdf/basic/Graph.h"
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


def get_ogdf_info():
    from ogdf_python import __version__
    cppinclude("ogdf/basic/System.h")
    data = {
        "ogdf_path": get_library_path() or "unknown",
        "ogdf_include_path": get_ogdf_include_path() or "unknown",
        "ogdf_version": get_macro("OGDF_VERSION").strip('"'),
        "ogdf_python_version": __version__,
        "ogdf_debug": get_macro("OGDF_DEBUG") is not None,
        "ogdf_build_debug": ogdf.debugMode,
        "debug": get_macro("NDEBUG") is None,
        "numberOfProcessors": ogdf.System.numberOfProcessors(),
        "cacheSize": ogdf.System.cacheSizeKBytes() * 1024,
        "cacheLineBytes": ogdf.System.cacheLineBytes(),
        "pageSize": ogdf.System.pageSize(),
        "physicalMemory": ogdf.System.physicalMemory(),
        "availablePhysicalMemory": ogdf.System.availablePhysicalMemory(),
        "memoryUsedByProcess": ogdf.System.memoryUsedByProcess(),
        "memoryAllocatedByMalloc": ogdf.System.memoryAllocatedByMalloc(),
        "memoryInFreelistOfMalloc": ogdf.System.memoryInFreelistOfMalloc(),
        "memoryAllocatedByMemoryManager": ogdf.System.memoryAllocatedByMemoryManager(),
        "memoryInGlobalFreeListOfMemoryManager": ogdf.System.memoryInGlobalFreeListOfMemoryManager(),
        "memoryInThreadFreeListOfMemoryManager": ogdf.System.memoryInThreadFreeListOfMemoryManager(),
        "cpuFeatures": {
            "MMX": ogdf.System.cpuSupports(ogdf.CPUFeature.MMX),
            "SSE": ogdf.System.cpuSupports(ogdf.CPUFeature.SSE),
            "SSE2": ogdf.System.cpuSupports(ogdf.CPUFeature.SSE2),
            "SSE3": ogdf.System.cpuSupports(ogdf.CPUFeature.SSE3),
            "SSSE3": ogdf.System.cpuSupports(ogdf.CPUFeature.SSSE3),
            "SSE4_1": ogdf.System.cpuSupports(ogdf.CPUFeature.SSE4_1),
            "SSE4_2": ogdf.System.cpuSupports(ogdf.CPUFeature.SSE4_2),
            "VMX": ogdf.System.cpuSupports(ogdf.CPUFeature.VMX),
            "SMX": ogdf.System.cpuSupports(ogdf.CPUFeature.SMX),
            "EST": ogdf.System.cpuSupports(ogdf.CPUFeature.EST),
        },
        "isUnix": get_macro("OGDF_SYSTEM_UNIX") is not None,
        "isWindows": get_macro("OGDF_SYSTEM_WINDOWS") is not None,
        "isOSX": get_macro("OGDF_SYSTEM_OSX") is not None,
        "system": conf_which("System"),
        "LPsolver": conf_which("LPSolver"),
        "memoryManager": conf_which("MemoryManager"),
    }
    if hasattr(ogdf.System, "peakMemoryUsedByProcess"):
        data["peakMemoryUsedByProcess"] = ogdf.System.peakMemoryUsedByProcess()
    return data
