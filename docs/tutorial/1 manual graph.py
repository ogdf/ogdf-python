# %%
# The following line loads the ogdf-python interface to the ogdf:
from ogdf_python import ogdf

# The next line enables interactive Graph displays for the whole notebook:
# %matplotlib widget

# Now, let's create out first OGDF Graph!

G = ogdf.Graph()
c = G.newNode()
print(c)
for i in range(4):
    n = G.newNode()
    e = G.newEdge(c, n)
    print(i, n, e)

G  # having G on the last line of a code cell displays the graph interactively

# %%
prev = first = None

# we can continue using all variables defined in cells run before this cell
for n in G.nodes:
    print(n)  # str(n) gives full information, n.index() only short id

    if n.degree() != 1:  # ignore the center node
        continue

    if prev is not None:
        e = G.newEdge(prev, n)
        print(e)
    else:
        first = n

    prev = n

if prev != first:
    G.newEdge(prev, first)

G  # display the updated graph

# %%
for e in list(G.edges):  # make a copy before making changes
    if e.isIncident(c) and e.index() % 2 == 0:
        G.delEdge(e)  # invalidates `e` and iterators into G.edges

G  # also check the interactive displays above, they updated automatically!

# %%
help(G)  # also check out `n` and `e`!
