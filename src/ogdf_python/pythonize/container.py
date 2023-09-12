def GraphObjectContainer_byindex(self, idx):
    for e in self:
        if e.index() == idx:
            return e
    raise IndexError("Container has no element with index %s." % idx)


def advance_iterator(self):
    if not self.valid():
        raise StopIteration()
    val = self.__deref__()
    self.__preinc__()
    return val


def cpp_iterator(self):
    it = self.begin()
    while it != self.end():
        yield it.__deref__()
        it.__preinc__()


def iterable_getitem(self, key):
    if isinstance(key, slice):
        indices = range(*key.indices(len(self)))
        elems = []
        try:
            next_ind = next(indices)
            for i, e in enumerate(self):
                if i == next_ind:
                    elems.append(e)
                    next_ind = next(indices)
        except StopIteration:
            pass
        return elems
    elif isinstance(key, int):
        if key < 0:
            key += len(self)
        if key < 0 or key >= len(self):
            raise IndexError("The index (%d) is out of range." % key)
        for i, e in enumerate(self):
            if i == key:
                return e
    else:
        raise TypeError("Invalid argument type %s." % type(key))


def get_adjentry_array_keys(aea):
    for e in aea.graphOf().edges:
        yield e.adjSource()
        yield e.adjTarget()


ArrayKeys = {
    "Node": lambda na: na.graphOf().nodes,
    "Edge": lambda ea: ea.graphOf().edges,
    "AdjEntry": get_adjentry_array_keys,
    "Cluster": lambda ca: ca.graphOf().clusters,
    "Face": lambda fa: fa.embeddingOf().faces,
}
