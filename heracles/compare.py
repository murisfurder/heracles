"""
The pourpose of this module is to provide the set of tools required to
build a custom tree from configuration parameters that can be merged with
the existing tree of a parsed configuration file.
"""

from heracles.tree import ListTree
from heracles.exceptions import HeraclesCompareError, \
        HeraclesSortedKeysDictError

def check_dict(obj):
    return hasattr(obj, "items") and hasattr(getattr(obj, "items"), "__call__")

class MultipleKeysDict(dict):
    sorted_multiple_keys = ()
    unsorted_multiple_keys = ()

    def __init__(self, *args, **kwords):
        l = len(args)
        if l == 1:
            self._load_data(args[0])
        elif l > 1:
            raise TypeError("MultipleKeysDict expected at most 1 arguments, got %d" % l)
        self._load_data(kwords)

    def _load_data(self, data):
        for name, value in data.items():
            if name in self.sorted_multiple_keys:
                if hasattr(value, "__iter__"):
                    self._setitem(name, list(value))
                else:
                    self._setitem(name, [value])
            elif name in self.unsorted_multiple_keys:
                if hasattr(value, "__iter__"):
                    self._setitem(name, set(value))
                else:
                    self._setitem(name, set((value,)))
            else:
                self._setitem(name, value)

    def _setitem(self, name, value):
        super(MultipleKeysDict, self).__setitem__(name, value)

    def __setitem__(self, name, value):
        if name in self.sorted_multiple_keys:
            if name in self:
                self[name].append(value)
            else:
                self._setitem(name, [value])
        elif name in self.unsorted_multiple_keys:
            if name in self:
                self[name].add(value)
            else:
                self._setitem(name, set((value,)))
        else:
            self._setitem(name, value)

class SortedKeysDict(dict):
    key_order = ()

    def _keys(self):
        return super(SortedKeysDict, self).keys()

    def check(self):
        if not set(self.key_order).issubset(super(SortedKeysDict, self).keys()):
            raise HeraclesSortedKeysDictError()

    def iternotorderedkeys(self):
        self.check()
        for k in set(self._keys()).difference(set(self.key_order)):
            yield k

    def notorderedkeys(self):
        return list(self.iternotorderedkeys())

    def iterkeys(self):
        self.check()
        for k in self.key_order:
            yield k
        for k in self.iternotorderedkeys():
            yield k

    def keys(self):
        return list(self.iterkeys())

    def iteritems(self):
        self.check()
        for k in self.iterkeys():
            yield k, self[k]

    def items(self):
        return list(self.iteritems())


    def itervalues(self):
        for k in self.iterkeys():
            yield self[k]

    def values(self):
        return list(self.itervalues())


def update_tree(tree, ):
    pass
    





