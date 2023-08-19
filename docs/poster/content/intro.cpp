using namespace ogdf;

#include <ogdf/basic/graph_generators.h>
#include <ogdf/layered/SugiyamaLayout.h>
#include <ogdf/fileformats/GraphIO.h>

int main() {
  Graph G;
  GraphAttributes GA(G);
  randomPlanarTriconnectedGraph(G, 10, 20);
  
  for (node n : G.nodes)
    GA.label[n] = "N" + string(n.index());
  
  SugiyamaLayout SL;
  SL.call(GA);
  GraphIO::write(GA, "output.svg");
  
  return 0;
}
