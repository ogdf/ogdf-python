%%cpp

// Include C++ Code in your Python Notebook
std::cout << "Hello World from C++!" << std::endl;

ogdf::Graph G; // created in C++
int width = 3, height = 3;
ogdf::gridGraph(G, width, height, true, false);