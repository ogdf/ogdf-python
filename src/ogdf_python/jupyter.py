import sys

import cppyy

ip = None
if "IPython" in sys.modules:
    from IPython import get_ipython

    ip = get_ipython()

if ip is not None:
    from IPython.core.magic import register_cell_magic

    cppyy.cppdef("""
#include <sstream>
#include <streambuf>
#include <iostream>

namespace ogdf_pythonization {
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
}

std::ostringstream gCapturedStderr;
std::streambuf* gOldStderrBuffer = nullptr;

static void BeginCaptureStderr() {
    gOldStderrBuffer = std::cerr.rdbuf();
    std::cerr.rdbuf(gCapturedStderr.rdbuf());
}

static std::string EndCaptureStderr() {
    std::cerr.rdbuf(gOldStderrBuffer);
    gOldStderrBuffer = nullptr;

    std::string capturedStderr = std::move(gCapturedStderr).str();

    gCapturedStderr.str("");
    gCapturedStderr.clear();

    return capturedStderr;
}
}
""")


    @register_cell_magic
    def cpp(line, cell):
        """
        might yield "function definition is not allowed here" for some multi-part definitions
        use `cppdef` instead if required
        https://github.com/jupyter-xeus/xeus-cling/issues/40
        """
        cppyy.gbl.ogdf_pythonization.BeginCaptureStdout()
        cppyy.gbl.ogdf_pythonization.BeginCaptureStderr()
        try:
            cppyy.cppexec(cell)
        finally:
            print(cppyy.gbl.ogdf_pythonization.EndCaptureStdout(), end="")
            print(cppyy.gbl.ogdf_pythonization.EndCaptureStderr(), file=sys.stderr, end="")


    @register_cell_magic
    def cppdef(line, cell):
        cppyy.cppdef(cell)
