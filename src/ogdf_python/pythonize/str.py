# TODO add proper __str__ and __repr__ for (Cluster)Graph(Attributes), node, edge, adjEntry, (Node|Edge|AdjEntry|...)Array, (S)List(Pure), Array

def node_str(node):
    return "n%s" % node.index()


def node_repr(node):
    adjs = ["e%s%sn%s" % (adj.theEdge().index(), "->" if adj.isSource() else "<-", adj.twinNode().index())
            for adj in node.adjEntries]
    return "n%s °(%si+%so=%s) [%s]" % (node.index(), node.indeg(), node.outdeg(), node.degree(), ", ".join(adjs))


def edge_str(edge):
    return "e%s" % edge.index()


def edge_repr(edge):
    return "n%s--e%s->n%s" % (edge.source().index(), edge.index(), edge.target().index())


def adjEntry_str(adj):
    return "a%s" % adj.index()


def adjEntry_repr(adj):
    if adj.isSource():
        return "(n%s--a%s)e%s->n%s" % (
            adj.theNode().index(), adj.index(), adj.theEdge().index(), adj.twinNode().index())
    else:
        return "(n%s<-a%s)e%s--n%s" % (
            adj.theNode().index(), adj.index(), adj.theEdge().index(), adj.twinNode().index())
