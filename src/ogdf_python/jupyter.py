import cppyy
import sys

ip = None
if "IPython" in sys.modules:
    from IPython import get_ipython

    ip = get_ipython()

if ip is not None:
    from IPython.core.magic import register_cell_magic


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
