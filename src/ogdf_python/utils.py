from ogdf_python.loader import *

__all__ = ["is_nullptr", "typed_nullptr"]

_capture_stdout = """
std::ostringstream gCapturedStdout;
std::streambuf* gOldStdoutBuffer = nullptr;

static void BeginCaptureStdout() {
    gOldStdoutBuffer = std::cout.rdbuf();
    std::cout.rdbuf(gCapturedStdout.rdbuf());
}

static std::string EndCaptureStdout() {
    std::cout.rdbuf(gOldStdoutBuffer);
    gOldStdoutBuffer = nullptr;

    std::string capturedStdout = std::move(gCapturedStdout).str();

    gCapturedStdout.str("");
    gCapturedStdout.clear();

    return capturedStdout;
}"""

cppyy.cppdef("""
#include <sstream>
#include <streambuf>
#include <iostream>

namespace ogdf_pythonization {
%s

%s
}
""" % (_capture_stdout, _capture_stdout.replace("out", "err")))


def is_nullptr(o):
    return cppyy.ll.addressof(o) == 0


def typed_nullptr(klass):
    if isinstance(klass, type(ogdf.node)):  # cppyy.TypedefPointerToClass
        return klass()  # returns typed nullptr
    return cppyy.bind_object(cppyy.nullptr, klass)
