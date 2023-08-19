from cppyy import gbl as cpp  # namespace with all C++ variables

G = cpp.G  # used from Python
GA = ogdf.GraphAttributes(G, ogdf.GraphAttributes.all)

for n in G.nodes:
    GA.label[n] = str(n.index())
    GA.x[n] = (n.index() % cpp.width) * 50
    GA.y[n] = (n.index() // cpp.height) * 50

middle = G.numberOfNodes() // 2
GA.width[G.nodes[middle]] = 40
GA.height[G.nodes[middle]] = 40

GA