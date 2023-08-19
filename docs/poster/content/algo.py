discovery = ogdf.NodeArray[int](G, -1)
finish = ogdf.NodeArray[int](G, -1)
predecessor = ogdf.NodeArray[ogdf.node](G, nullptr)

time = 0

def dfs_visit(u):
	global time

	time += 1
	discovery[u] = time

	for adj in u.adjEntries:
		v = adj.twinNode()
		if adj.isSource() and discovery[v] < 0:
			predecessor[v] = u
			dfs_visit(v)

	time += 1
	finish[u] = time

for n in G.nodes:
	if discovery[n] < 0:
		dfs_visit(n)