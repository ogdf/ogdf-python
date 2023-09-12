import functools
import tempfile

import cppyy
import itertools
import sys

SVGConf = None


def wrap_GraphIO(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = cppyy.gbl.ogdf.GraphIO.logger
        levels = {
            l: getattr(logger, l)()
            for l in [
                "globalLogLevel",
                "globalInternalLibraryLogLevel",
                "globalMinimumLogLevel",
                "localLogLevel",
            ]
        }
        logMode = logger.localLogMode()
        statMode = logger.globalStatisticMode()
        ret = stdout = stderr = None

        try:
            logger.localLogMode(type(logger).LogMode.Global)
            logger.globalStatisticMode(False)
            for l in levels:
                getattr(logger, l)(type(logger).Level.Minor)

            cppyy.gbl.ogdf_pythonization.BeginCaptureStdout()
            cppyy.gbl.ogdf_pythonization.BeginCaptureStderr()
            try:
                ret = func(*args, **kwargs)
            finally:
                stdout = cppyy.gbl.ogdf_pythonization.EndCaptureStdout().decode("utf8", "replace").strip()
                stderr = cppyy.gbl.ogdf_pythonization.EndCaptureStderr().decode("utf8", "replace").strip()

        finally:
            logger.localLogMode(logMode)
            logger.globalStatisticMode(statMode)
            for l, v in levels.items():
                getattr(logger, l)(v)

            if stdout and logger.is_lout(logger.Level.Medium):
                print(stdout)
            if stderr:
                print(stderr, file=sys.stderr)

        if not ret:
            args = ', '.join(itertools.chain(map(repr, args), (f"{k}={v!r}" for k, v in kwargs.items())))
            msg = f"GraphIO.{func.__name__}({args}) failed"
            if stdout or stderr:
                msg += ":"
                if stdout:
                    msg += "\n" + stdout
                if stderr:
                    msg += "\n" + stderr
            else:
                msg += " for unknown reason. Does the file exist?"
            raise IOError(msg)
        else:
            return ret

    return wrapper


def renderGraph(G):
    cppyy.include("ogdf/planarity/PlanarizationGridLayout.h")
    ogdf = cppyy.gbl.ogdf
    GA = ogdf.GraphAttributes(G, ogdf.GraphAttributes.all)
    ogdf.PlanarizationGridLayout().call(GA)
    for n in G.nodes:
        GA.label[n] = str(n.index())
    return GA


def renderClusterGraph(CG):
    cppyy.include("ogdf/cluster/ClusterPlanarizationLayout.h")
    ogdf = cppyy.gbl.ogdf
    CGA = ogdf.ClusterGraphAttributes(CG, ogdf.ClusterGraphAttributes.all)
    cppyy.gbl.ogdf_pythonization.BeginCaptureStdout()
    try:
        ogdf.ClusterPlanarizationLayout().call(CG.getGraph(), CGA, CG)
    finally:
        stdout = cppyy.gbl.ogdf_pythonization.EndCaptureStdout().decode("utf8", "replace").strip()
    for n in CG.getGraph().nodes:
        CGA.label[n] = str(n.index())
    return CGA


def GraphAttributes_to_svg(self):
    global SVGConf
    if SVGConf is None:
        SVGConf = cppyy.gbl.ogdf.GraphIO.SVGSettings()
        SVGConf.margin(50)
        SVGConf.bezierInterpolation(False)
        # SVGConf.curviness(0.1)
    with tempfile.NamedTemporaryFile("w+t", suffix=".svg", prefix="ogdf-python-") as f:
        os = cppyy.gbl.std.ofstream(f.name)
        cppyy.gbl.ogdf.GraphIO.drawSVG(self, os, SVGConf)
        os.close()
        return f.read()


def Graph_to_svg(self):
    return GraphAttributes_to_svg(renderGraph(self))


def ClusterGraph_to_svg(self):
    return GraphAttributes_to_svg(renderClusterGraph(self))
