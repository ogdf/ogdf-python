# %%
# %matplotlib widget
from ogdf_python import ogdf

# Let's start with a clique of 4 (pairwise connected) nodes...

G = ogdf.Graph()
N = [G.newNode() for _ in range(4)]
for u in N:
    for v in N:
        if u.index() < v.index():
            G.newEdge(u, v)

G

# %%
# We can view the graph as a list of nodes together with a list of edges
nodes_str = ", ".join(str(n.index()) for n in G.nodes)
print("Nodes: [", nodes_str, "]")
print("Edges:")
for e in G.edges:
    print(f"{e.index()}: {e.source().index()} -> {e.target().index()}")

# %%
# Alternatively, we can also iterate over the adjacency lists of each node
print("Adjacencies...")
for u in G.nodes:
    print(f"...of {u}:")
    for adj in u.adjEntries:  # u.adjEntries wraps the edges incident to u
        # each adjEntry `adj` has methods for accessing the adjacent node or incident edge
        # see also the image below and check out help(adj)
        v = adj.twinNode()
        e = adj.theEdge()

        print(
            " ", e.index(), ": ", u.index(), "->" if adj.isSource() else "<-", v.index()
        )

# note that the order of adjEntries is not reflected when displaying a graph by having `G` on a cell's last line
# likewise, reordering nodes and edges in the interactive preview doesn't change the order

# %% [markdown]
# ![adjList.png](attachment:adjList.png)


# %%
def dump(o):
    # print some infos about `o`
    print(f"{type(o).__name__} '{o.index()}': {o}")


# try to guess the types of the following objects before running this cell!
dump(G.nodes.tail())
dump(G.nodes.tail().adjEntries.head())
dump(G.nodes.tail().adjEntries.head().theEdge())

# %%
# is there a planar drawing where the order of incident edges for each node
# corresponds to the order given in n.adjEntries?
# -> if yes G represents a combinatorial (planar) embedding
G.representsCombEmbedding()

# %%
# print the current orders of incident edges
# why does this represent no combinatorial embedding?
for n in G.nodes:
    print(n)

# %%
print(N[1])
G.reverseAdjEdges(N[1])  # maybe flipping this node helps?
print(N[1])
print("Planar?", G.representsCombEmbedding())

# %%
G.reverseAdjEdges(N[3])  # but flipping this one too should do the trick!
print(N[3])
print("Planar?", G.representsCombEmbedding())
print("\n".join(str(n) for n in G.nodes))  # try to find a drawing with these orders

# %%
# in the drawing, a white region enclosed by edges is called (inner) face
# the white area around the drawing is the outer face

# if G represents a combinatorial embedding, we can walk along the edges delimiting a face

n = N[0]
adj = first = n.adjEntries.head()
print(adj)  # we will walk the face to the right of this adjEntry

while (
    adj.clockwiseFaceSucc() != first
):  # proceed clockwise until reaching the beginning again
    # clockwiseFaceSucc returns the same object as jumping to the adjEntry on the other side of
    # the edge with twin() and continuing on to the predecessing adjEntry around the twin node.
    # see also the image below
    print("next: ", adj.twin(), adj.twin().cyclicPred(), adj.clockwiseFaceSucc())

    adj = adj.clockwiseFaceSucc()
    print(adj)

print("next: ", adj.twin(), adj.twin().cyclicPred(), adj.clockwiseFaceSucc())
# try to locate this face in your drawing!

# %% [markdown]
# ![faceOrder.png](attachment:faceOrder.png)

# %%
# instead of manually trying to find a planar embedding, OGDF can do that for us!
embed = ogdf.planarEmbed(G)
# check out the message of the thrown exception, it should help you fixing the issue ;)

print("Succeeded in embedding it planarly?", embed)  # well, that should be easy now...
print("Is it actually planar now?", G.representsCombEmbedding())
print("\n".join(str(n) for n in G.nodes))
# the embedding is different!?
# how does this embedding differ from the one we found?

# %%
