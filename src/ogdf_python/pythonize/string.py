from ogdf_python.utils import *


def node_repr(node):
    if is_nullptr(node):
        return "typed_nullptr(ogdf.node)"
    return "G.nodes.byid(%s)" % node.index()


def node_str(node):
    if is_nullptr(node):
        return "nullptr (of type ogdf::node)"
    adjs = ["e%s%sn%s" % (adj.theEdge().index(), "->" if adj.isSource() else "<-", adj.twinNode().index())
            for adj in node.adjEntries]
    return "n%s °(%si+%so=%s) [%s]" % (node.index(), node.indeg(), node.outdeg(), node.degree(), ", ".join(adjs))


def edge_repr(edge):
    if is_nullptr(edge):
        return "typed_nullptr(ogdf.edge)"
    return "G.edges.byid(%s)" % edge.index()


def edge_str(edge):
    if is_nullptr(edge):
        return "nullptr (of type ogdf::edge)"
    return "n%s--e%s->n%s" % (edge.source().index(), edge.index(), edge.target().index())


def adjEntry_repr(adj):
    if is_nullptr(adj):
        return "typed_nullptr(ogdf.adjEntry)"
    if adj.isSource():
        return "G.edges.byid(%s).adjSource()" % adj.theEdge().index()
    else:
        return "G.edges.byid(%s).adjTarget()" % adj.theEdge().index()


def adjEntry_str(adj):
    if is_nullptr(adj):
        return "nullptr (of type ogdf::adjEntry)"
    if adj.isSource():
        return "(n%s--a%s)e%s->n%s" % (
            adj.theNode().index(), adj.index(), adj.theEdge().index(), adj.twinNode().index())
    else:
        return "(n%s<-a%s)e%s--n%s" % (
            adj.theNode().index(), adj.index(), adj.theEdge().index(), adj.twinNode().index())
