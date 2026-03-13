# %% [markdown]
# In this notebook, we'll show how to gradually migrate Python code to more efficient C++ code, while keeping the interactivity of Jupyter's notebooks. We'll use the "iterative DFS" from the Python tutorial as example for the migration, so make sure to have that notebook open for comparison! First, we'll create our example graph (in plain Python for simplicity):

# %%
# %matplotlib widget
from ogdf_python import ogdf, cppinclude

cppinclude("ogdf/basic/graph_generators/randomized.h")
cppinclude("ogdf/layered/SugiyamaLayout.h")

G = ogdf.Graph()
ogdf.setSeed(1)
ogdf.randomPlanarTriconnectedGraph(G, 10, 20)
G2 = ogdf.Graph()
ogdf.randomPlanarTriconnectedGraph(G2, 5, 10)
G.insert(G2)

GA = ogdf.GraphAttributes(G, ogdf.GraphAttributes.all)
SL = ogdf.SugiyamaLayout()
SL.call(GA)
GA.rotateLeft90()
GA

# %%
# There are multiple ways to include C++ code in your Python notebook.
# First, we'll have a look at the `cppexec` and `cppdef` functions provided by `ogdf_python`.
from ogdf_python import cppexec, cppdef

cppexec(""" // here comes the C++ code as a string!

// this is the C++ version of `print(...)`:
std::cout << "Hello World!" << std::endl;

// hint: you can print variables by simply putting them in the chain of `<<`s
int myInt = 42;
std::cout << "My number is: " << myInt << std::endl;

""") # triple-quotes are nice for hassle-free multi-line strings!

# %% [markdown]
# Note that the value `True` returned by `cppexec` simply means that the code was successfully executed.
# If you don't want to execute the C++ code right away (like in a `main` method), but just declare variables and functions, `cppdef` is suited better (but both should work the same in most cases).
# As you might know, C++ is (unlike Python) a statically-typed language and we thus need to declare our variable `myInt` as actually being an `int` before we can use it.
#
# Now, lets declare the first variable used by our DFS in C++. In Python this looked like this:
# ```python
# order = [] # order of visited nodes
# ```
# The usual C++ type for lists is [`std::vector`](https://en.cppreference.com/w/cpp/container/vector). Again, due to C++ being statically typed, we need to tell the vector which kind of objects it will contain - Graph nodes in this case.
# Note that we don't need to call a constructor or assign an object instance to the variable, as C++ does that automatically.
# Manually creating the object similar to what is needed in Python is only done for pointer variables with manual memory management, which is not recommended (and thus not shown here).

# %%
cppdef(""" // declare the first two variables used by the DFS

std::vector<ogdf::node> order; // order of visited nodes

""")

# variables declared in C++ can be accessed via the `cppyy.gbl` object
from ogdf_python import cppyy # or simply `from ogdf_python import *` in the future to get everything at once
g = cppyy.gbl # shorten the name a little

g.order

# %% [markdown]
# That's not a super useful string representation, but that's simply C++. Still, the vector can be used perfectly fine from Python, as you'll see in the cell below. The functions are sometimes a little bit different, check out the [C++ reference](https://en.cppreference.com/w/cpp/container/vector) for details!
#
# Note that if you execute above cell multiple times, you'll get an error about the redefinition of the variable `order` - as you would when declaring two variables with the same name in a single C++ file.
# If you actually want to overwrite the previous declaration, you can use `cppexec`, which is fine with overwriting previous declarations.

# %%
g.order.push_back(G.nodes[3])

print("New length:", len(g.order))
print("The node is:", g.order[0])
print("Is that the right one?",
      g.order[0] == G.nodes[3])

g.order.clear()
print("Is there something left?", bool(g.order))

# %% [markdown]
# If you write a lot of C++ code (as we will do in the following), it might be more comfortable to no longer need to wrap everything in strings and function calls and write whole cells with C++ code.
# You can do that by putting `%%cpp` (for `cppexec(...)`) or `%%cppdef` (for `cppdef(...)`) in the first line of your cell. Note that these non-standard [cell magics](https://ipython.readthedocs.io/en/stable/interactive/magics.html) only work after ogdf-python has been imported.
#
# But now back to the problem at hand and the `cppdef` in the previous cell.
# The `<ogdf::node>` after the class name of `order` is called "template parameter".
# We've actually already seen that kind of thing when we told the C++ `ogdf.NodeArray` used for the indices assigned by the DFS that it will store values of type `int`. So the Python statement `index = ogdf.NodeArray[int](G, -1)` becomes `ogdf.NodeArray<int> dfs_index(G, -1);` in C++:

# %%
# # %%cpp

// the whole cell contains C++ code (which will be passed to `cppexec`)

ogdf::NodeArray<int> dfs_index(G, -1); // index in order

# %% [markdown]
# Dang! `error: use of undeclared identifier 'G'` tells us that C++ can't find the variable `G`.
# This is because, while Python can easily access things declared in C++ via `cppyy.gbl`, the reverse is unfortunately not true.
# We either need to declare everything we want to use from C++ also in C++, or put everything into C++ functions and pass in the Python objects as function parameters (with the right type declarations on arguments).
# Here, we have a third alternative: we can pass in the constructor argument later by calling the `NodeArray.init` method (which does the same thing as the constructor) from Python.

# %%
cppdef("""
ogdf::NodeArray<int> dfs_index;
""")

g.dfs_index.init(G, -1)

# %%
# # %%cpp

// As we were using the `todo` list as stack, it can also be easily translated to a `vector`:

std::vector<std::pair<ogdf::node, ogdf::edge>> todo;

# %% [markdown]
# Now let's translate the first part of our actual DFS code.

# %%
# # %%cppdef

bool find_next(ogdf::Graph& G) { // pass the graph from Python as function argument (by reference!)
    for (ogdf::node n : G.nodes) { // foreach needs types or at least `auto` as type
        if (dfs_index[n] == -1) {
            todo.emplace_back(n, nullptr); // calls the tuple constructor "inplace", i.e., without copying
            return true;
        }
    }
    return false;
}

# %% [markdown]
# The final mode for including C++ code is by writing it to an external file and including it with `cppinclude`. Note that similar to `cppdef`, this mode doesn't allow redifinitions and thus should only be used for code that doesn't need frequent changes. Still, this is especially useful if you also want to directly re-use the code in a pure C++ environment. The [`%%writefile` cell magic](https://ipython.readthedocs.io/en/stable/interactive/magics.html#cellmagic-writefile) below will create the file for you, which we can `cppinclude` in the cell after.

# %%
# # %%writefile dfs_step.h

using namespace ogdf; // stop prefixing everything with ogdf::

void dfs_step(GraphAttributes& GA) {// compare this to our previous Python implementation!
    // `pred` is the edge via which we found `u`, or nullptr if `u` is a root
    edge pred = todo.back().second;
    node u = todo.back().first;
    
    // insert u into order and set its index
    dfs_index[u] = order.size();
    order.emplace_back(u);
    
    // update the drawing
    GA.label(u) = std::to_string(dfs_index[u]);
    if (pred)
        GA.strokeColor(pred) = Color("#F00");
    // note: in Python, GraphAttributes need square brackets, in C++ round parentheses
    
    // remove already processed nodes from stack
    while (!todo.empty() && dfs_index[todo.back().first] >= 0)
        todo.pop_back();
        
    // add unprocessed neighbors from stack
    for (auto adj : u->adjEntries) {
        // C++ can often infer automatically variable types by using `auto`
        // ogdf::node, edge and adjEntry are actually pointers, so use `->` to access members
        auto v = adj->twinNode();
        if (dfs_index[v] == -1)
            todo.emplace_back(v, adj->theEdge());
    }
}

# %%
cppinclude("dfs_step.h")

# import the functions and provide the arguments
find_next = lambda: g.find_next(G)
dfs_step = lambda: g.dfs_step(GA)

# The remainder of this notebook stays the same...
def dump(): # utility function for easily displaying the current state
    print("Order", ", ".join(str(n.index()) for n in g.order))
    print("Todo", ", ".join(str(n.index()) for n,p in g.todo))
    return GA


# %%
# Run this and the following cells one after another to see the DFS progress...
find_next()
dump()

# %%
dfs_step()
dump()

# %%
dfs_step()
dump()

# %%
dfs_step()
dump()

# %%
dfs_step()
dump()

# %%
# The widget works as before!

# enable the interactive widget
# # %matplotlib widget
import ipywidgets
from ogdf_python.matplotlib import MatplotlibGraph

w = MatplotlibGraph(GA) # widget for displaying a drawing
w_todo = ipywidgets.Label() # text labels
w_order = ipywidgets.Label()
b_dfs = ipywidgets.Button(description="Step") # interactive buttons
b_next = ipywidgets.Button(description="Next Component")
b_reset = ipywidgets.Button(description="Reset")

def update():
    # update all UI elements
    w.update_all()
    w_todo.value = "Todo: " + ", ".join(str(n.index()) for n,p in g.todo)
    w_order.value = "Order: " + ", ".join(str(n.index()) for n in g.order)
    b_dfs.disabled = g.todo.empty()

def b_dfs_click(b):
    # when clicking the "Step" button, execute one DFS step and update the UI
    dfs_step()
    update()
b_dfs.on_click(b_dfs_click) # functions are objects, too!

def b_next_click(b):
    # continue to the next (or first) connected component
    find_next()
    update()
b_next.on_click(b_next_click)

def b_reset_click(b):
    # reset the DFS to the initial empty state
    g.order.clear()
    g.dfs_index.fill(-1)
    g.todo.clear()
    to_reset = ogdf.GraphAttributes.edgeStyle | ogdf.GraphAttributes.nodeLabel
    GA.destroyAttributes(to_reset)
    GA.addAttributes(to_reset)
    update()
b_reset.on_click(b_reset_click)


update()
# V- and HBoxes arrange multiple UI widgets next to each other
# as for G and GA, the UI element on the last line of a cell will be rendered below it
ipywidgets.VBox([ipywidgets.HBox([b_dfs, b_next, b_reset]), w_todo, w_order, w.ax.figure.canvas])
