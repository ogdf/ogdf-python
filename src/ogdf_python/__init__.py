from ogdf_python.loader import *

ogdf  # keep imports in this order

from ogdf_python.utils import *
from ogdf_python.info import *

import ogdf_python.doxygen
import ogdf_python.pythonize
import ogdf_python.jupyter

__keep_imports = [
    ogdf_python.doxygen,
    ogdf_python.pythonize,
    ogdf_python.jupyter,
]

__version__ = "0.3.4"
__all__ = ogdf_python.loader.__all__ + ogdf_python.utils.__all__ + ogdf_python.info.__all__

try:
    import matplotlib
except ImportError:
    pass
else:
    from ogdf_python.matplotlib import *

    __all__ += ogdf_python.matplotlib.__all__
