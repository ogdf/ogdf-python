from ogdf_python.loader import *

__all__ = ["is_nullptr", "typed_nullptr"]


def is_nullptr(o):
    return cppyy.ll.addressof(o) == 0


def typed_nullptr(klass):
    if isinstance(klass, type(ogdf.node)):  # cppyy.TypedefPointerToClass
        return klass()  # returns typed nullptr
    return cppyy.bind_object(cppyy.nullptr, klass)
