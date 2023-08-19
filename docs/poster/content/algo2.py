class DFS:
	def __init__(self, G):
		self.G = G

		self.discovery = \
			ogdf.NodeArray[int](G, -1)
		self.finish = \
			ogdf.NodeArray[int](G, -1)
		self.predecessor = \
			ogdf.NodeArray[ogdf.node](G, nullptr)

		self.time = 0




	def dfs_visit(self,u):
		self.time += 1
		self.discovery[u] = self.time

		for adj in u.adjEntries:
			v = adj.twinNode()
			if adj.isSource() and \
					self.discovery[v] < 0:
				self.predecessor[v] = u
				self.dfs_visit(v)

		self.time += 1
		self.finish[u] = self.time

	def dfs(self):
		for n in self.G.nodes:
			if self.discovery[n] < 0:
				self.dfs_visit(n)
