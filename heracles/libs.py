import os
from platform import system
import ctypes
import ctypes.util
from heracles.util import get_heracles_path
from heracles.exceptions import HeraclesError

LIBRARY_NAME = "libheracles"
LIBRARY_DIR = "libs"

def get_library_name():
    s = system()
    if s == "Linux":
        ext = "so"
    elif s == "Darwin":
        ext = "a"
    elif s == "nt":
        ext = "dll"
    else:
        raise HeraclesError("Unknown operating system")
    return LIBRARY_NAME + "." + ext

def get_library_path():
    import pdb; pdb.set_trace()
    h_path = get_heracles_path()
    library_name = get_library_name()
    return os.path.join(h_path, LIBRARY_DIR, library_name)

libheracles = ctypes.cdll.LoadLibrary(get_library_path())
