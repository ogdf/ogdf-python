cppinclude("avg_width.h") # load method from C++ file
print("The node widths are", list(GA.width()))
print("The average width is", cpp.avg_width(GA)) # call your own C++ functions from python