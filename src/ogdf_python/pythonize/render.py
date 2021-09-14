import tempfile

import cppyy

SVGConf = None


def GraphAttributes_to_html(self):
    global SVGConf
    if SVGConf is None:
        SVGConf = cppyy.gbl.ogdf.GraphIO.SVGSettings()
        SVGConf.margin(50)
        SVGConf.bezierInterpolation(True)
        SVGConf.curviness(0.3)
    with tempfile.NamedTemporaryFile("w+t", suffix=".svg", prefix="ogdf-python-") as f:
        os = cppyy.gbl.std.ofstream(f.name)
        cppyy.gbl.ogdf.GraphIO.drawSVG(self, os, SVGConf)
        os.close()
        return f.read()
