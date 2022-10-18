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

try:
    from ogdf_python_widget import _auto_enable
except ImportError:
    pass
else:
    _auto_enable()

__version__ = "0.1.5"
__all__ = ogdf_python.loader.__all__ + ogdf_python.utils.__all__ + ogdf_python.info.__all__

if __name__ == "__main__":
    from pprint import pprint

    pprint(get_ogdf_info())
