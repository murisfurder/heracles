import os
import ctypes as c
from fnmatch import fnmatch
from heracles.structs import struct_heracles, struct_tree, struct_lns_error
from heracles.exceptions import get_exception
from heracles.libs import libheracles
from heracles.raw import UnmanagedRawTree, ManagedRawTree
from heracles.tree import Tree
from heracles.util import get_heracles_path

LENS_PATH = "lenses"
PATH_SEP = ":"

class HeraclesLenses(object):
    def __get__(self, obj, obj_type=None):
        self.heracles = obj
        self._handle = obj._handle
        return self

    def __iter__(self):
        module = self._handle.contents.module
        while True:
            if not module:
                break
            lens = Lens(self.heracles, module)
            if lens.lens:
                yield lens
            module = module.contents.next

    def __getitem__(self, name):
        for module in self:
            if module.name == name:
                return module
        raise KeyError("Unable to find module %s" % name)

class Heracles(object):
    lenses = HeraclesLenses()

    def get_load_path(self, loadpath):
        if loadpath is None:
            loadpath = []
        base_lens_path = [os.path.join(get_heracles_path(), LENS_PATH)]
        return PATH_SEP.join(base_lens_path + loadpath)

    def __init__(self, loadpath=None, flags=0):
        if isinstance(loadpath, list):
            for path in loadpath:
                if not isinstance(path, str):
                    raise TypeError("loadpath items must be string")
        elif loadpath == None:
            pass
        else:
            raise TypeError("loadpath MUST be a string or None!")
        if not isinstance(flags, int):
            raise TypeError("flag MUST be a flag!")

        loadpath = self.get_load_path(loadpath)

        hera_init = libheracles.hera_init
        hera_init.restype = c.POINTER(struct_heracles)

        self._handle = hera_init(loadpath, flags)
        if not self._handle:
            raise RuntimeError("Unable to create Heracles object!")

        self.error = self._handle.contents.error.contents

    def catch_exception(self):
        exception = get_exception(self)
        if exception is not None:
            raise Exception

    def new_tree(self):
        tree = Tree()
        return tree

    def get_lens_by_path(self, path):
        for lens in self.lenses:
            if lens.check_path(path):
                return lens

    def __repr__(self):
        return "<Heracles object>"

    def __del__(self):
        hera_close = libheracles.hera_close
        hera_close(self._handle)

class Lens(object):
    def __init__(self, heracles, module):
        self.heracles = heracles
        self.module = module.contents
        self.name = self.module.name
        transform = self.module.autoload
        self.lens = transform.contents.lens if transform else None
        self.filter = transform.contents.filter if transform else None

    def _catch_error(self, err):
        if err:
            raise Exception(err.contents.message)

    def get(self, text):
        hera_get = libheracles.hera_get
        hera_get.restype = c.POINTER(struct_tree)
        error = c.POINTER(struct_lns_error)()
        tree_p = hera_get(self.lens, c.c_char_p(text), error)
        self._catch_error(error)
        return UnmanagedRawTree(tree_p, lens=self).build_tree()

    def put(self, tree, text):
        raw_tree = ManagedRawTree.build_from_tree(tree)
        hera_put = libheracles.hera_put
        hera_put.restype = c.c_char_p
        error = c.POINTER(struct_lns_error)()
        result = hera_put(self.lens, raw_tree.first, c.c_char_p(text), error)
        self._catch_error(error)
        return result

    def iter_filters(self):
        filter = self.filter
        while True:
            if not filter:
                break
            yield filter
            filter = filter.contents.next

    def check_path(self, path):
        positive = False
        negative = False
        for filter in self.iter_filters():
            res = check_filter(filter.contents, path)
            if res == True:
                positive = True
            if res == False:
                negative = True
        if negative or not positive:
            return False
        return True

    def __repr__(self):
        return "<Heracles.Lens '%s'>" % self.name

def check_filter(filter, path):
    match = fnmatch(path, filter.glob.contents.str)
    if match:
        return True if filter.include == 1 else False

