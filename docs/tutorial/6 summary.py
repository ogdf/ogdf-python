# %% [markdown]
# We have seen that there are three "levels" of graph information in OGDF:
#
# |   | Graph Information | OGDF Object       | Stored as               |
# |---|:------------------|:------------------|:------------------------|
# | 1 | Structure         | `Graph`           | `G.nodes, edges`        |
# | 2 | Embedding         | `Graph`           | Order of `n.adjEntries` |
# | 3 | Drawing           | `GraphAttributes` | `GA.x[n], GA.y[n],...`  |
#
# If information from a lower level is not needed, it can be simply left out or ignored.
# Modifying information on a higher level (e.g. deleting a node) will also affect the lower levels.
# Furthermore, we have seen how `Node-` and `EdgeArray`s can be used for annotating a graph with further information that wouldn't fit into `GraphAttributes`.

# %% [markdown]
# OGDF doesn't differentiate between directed and undirected graphs. Depending on whether the direction information is important or not for the respective use-case, different methods can be used:
#
# | Directed                              | Undirected                                |
# |--------------------------------------:|:------------------------------------------|
# | n.indeg(), n.outdeg()                 | n.degree()                                |
# | e.source(), e.target()                | e.nodes(), e.opposite(n), e.isIncident(n) |
# | e.isParallelDirected(e2)              | e.isParallelUndirected(e2)                |
# | --                                    | e.commonNode(e2)                          |
# | adj.isSource()                        | --                                        |
# | <is/make>ParallelFree(G)              | <is/make>ParallelFreeUndirected(G)        |
# | <is/make>Simple(G)                    | <is/make>SimpleUndirected(G)              |
# | isAcyclic(G), isArborescenceForest(G) | isAcyclicUndirected(G)                    |
# | isArborescence(G)                     | isTree(G)                                 |
# | randomDigraph(...)                    | randomSimpleGraph(...)                    |
#
# For `searchEdge(node v, node w, bool directed = false)`, the optional third argument decides whether an edge from `w` to `v` is also considered a valid result. Note that the function has `O(min(deg(v), deg(w)))` runtime in both cases.

# %% [markdown]
# Further interesting links to the OGDF docs:
# - [Graph](https://ogdf.github.io/doc/ogdf/classogdf_1_1_graph.html), [node](https://ogdf.github.io/doc/ogdf/classogdf_1_1_node_element.html), [edge](https://ogdf.github.io/doc/ogdf/classogdf_1_1_edge_element.html), [adjEntry](https://ogdf.github.io/doc/ogdf/classogdf_1_1_adj_element.html)
# - [Overview over the OGDF](https://ogdf.github.io/doc/ogdf/modules.html)
# - [GraphGenerators](https://ogdf.github.io/doc/ogdf/group__graph-generators.html): well-known graph classes (deterministic), randomized, as union/product/subgraph of other graphs
# - [simple](https://ogdf.github.io/doc/ogdf/simple__graph__alg_8h.html) and [extended Graph Algorithms](https://ogdf.github.io/doc/ogdf/extended__graph__alg_8h.html)
# - [LayoutModules](https://ogdf.github.io/doc/ogdf/classogdf_1_1_layout_module.html)

# %% [markdown]
# A common problem is using methods that modify the graph like `G.delEdge` while iterating over the edges,
# or methods that modify the embedding like `G.moveEdge` while iterating the adjEntries of a node.
# These methods invalidate both the passed edge / adjEntry and all iterators on the underlying list.
# Using the respective objects after calling these methods will lead to random segfaults or crashes and will generally not yield a working algorithm.
# To call the methods inside for-loops, create a copy of the list e.g. using `list(G.edges)`.

# %%
# The following example shows how to use nodes, edges or adjEntries as *values* for Arrays

import cppyy

null_edge = cppyy.bind_object(cppyy.nullptr, "ogdf::EdgeElement")

pred = ogdf.NodeArray["ogdf::edge"](G, null_edge)

...

if pred[n] == null_edge:
    ...
