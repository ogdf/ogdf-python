# Full Access to the Functionality of the OGDF with Python's Ease of Use

The Open Graph Drawing Framework (OGDF) is a C++ library containing a vast amount of algorithms and data structures for
automatic graph drawing.
However, while powerful the library is not easily accessible for new users and the nature of C++ makes implementing even
simple algorithms cumbersome to non-experts.
The `odgf-python` project remedies these problems by making the full OGDF available from Python.
This greatly reduces the overhead and complications when using the OGDF for the first time and unlocks a large ecosystem
of tools, for example the interactive computing Notebooks provided by Project Jupyter.
This is possible because the `ogdf-python` library aims to be an extensible building block, not a closed system.   

**Features**

- *No C++ skills needed*: The full OGDF API is available from Python.
- *Rapid Prototyping*: Python needs less boilerplate and allows more idiomatic constructions, without the need to configure and compile anything.
- *Iterative execution*: Jupyter Notebooks allow individual lines of code to be adapted and re-run, retaining all previous variable values.
- *Inline results*: Graphs are displayed right next to the code that generates them.
- *Interactive graph exploration*: The inline display allows interactive zooming and panning to easily explore the graph.
- *Extensible building block*: The library can be easily combined with other projects from the Python ecosystem, for example with `ipywidgets` to build portable user interfaces for graphs.

**Use-cases**

- iterative development of new graph algorithms
- step-by-step debugging of implemented algorithms
- visual editing of in-memory graphs and variables
- interactive visualization of algorithms for teaching
- flexible user interfaces for domain-specific application