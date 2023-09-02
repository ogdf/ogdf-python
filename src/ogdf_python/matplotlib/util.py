from matplotlib.path import Path

from ogdf_python.loader import *

__all__ = ["color", "fillPattern", "strokeType", "dPolylineToPath", "dPolylineToPathVertices", "new_figure"]


def color(c):
    return str(c.toString())


def fillPattern(fp):
    if not fp:
        return ""
    elif fp == ogdf.FillPattern.Solid:
        return ""
    elif fp == ogdf.FillPattern.Dense1:
        return "O"
    elif fp == ogdf.FillPattern.Dense2:
        return "o"
    elif fp == ogdf.FillPattern.Dense3:
        return "*"
    elif fp == ogdf.FillPattern.Dense4:
        return "."
    elif fp == ogdf.FillPattern.Dense5:
        return "OO"
    elif fp == ogdf.FillPattern.Dense6:
        return "**"
    elif fp == ogdf.FillPattern.Dense7:
        return ".."
    elif fp == ogdf.FillPattern.Horizontal:
        return "-"
    elif fp == ogdf.FillPattern.Vertical:
        return "|"
    elif fp == ogdf.FillPattern.Cross:
        return "+"
    elif fp == ogdf.FillPattern.BackwardDiagonal:
        return "\\"
    elif fp == ogdf.FillPattern.ForwardDiagonal:
        return "/"
    elif fp == ogdf.FillPattern.DiagonalCross:
        return "x"


def strokeType(st):
    if not st:
        return ""
    elif st == ogdf.StrokeType.Solid:
        return "-",
    elif st == ogdf.StrokeType.Dash:
        return "--",
    elif st == ogdf.StrokeType.Dot:
        return ":",
    elif st == ogdf.StrokeType.Dashdot:
        return "-.",
    elif st == ogdf.StrokeType.Dashdotdot:
        return (0, (3, 5, 1, 5, 1, 5)),


def dPolylineToPathVertices(poly):
    return [(p.m_x, p.m_y) for p in poly]


def dPolylineToPath(poly, closed=False):
    if closed:
        return Path(dPolylineToPathVertices(poly) + [(0, 0)], closed=True)
    else:
        return Path(dPolylineToPathVertices(poly), closed=False)


def new_figure(num=None):
    import matplotlib.pyplot as plt
    with plt.ioff():
        old_fig = plt.gcf()
        fig = plt.figure(num)
        plt.figure(old_fig)
    return fig
