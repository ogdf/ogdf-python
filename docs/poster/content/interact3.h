%%writefile avg_width.h
// these are the contents of file avg_width.h

// function implemented in C++ for efficiency
int avg_width(const ogdf::GraphAttributes &GA) {
    int sum = 0;
    for (auto n : GA.constGraph().nodes) {
        sum += GA.width(n);
    }
    return sum / GA.constGraph().numberOfNodes();
}