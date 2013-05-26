import os
import ctypes
import ctypes.util
from heracles.util import get_heracles_path

LIBRARY_NAME = "libheracles.so"
LIBRARY_DIR = "libs"

def get_library_path():
    h_path = get_heracles_path()
    return os.path.join(h_path, LIBRARY_DIR, LIBRARY_NAME)

libheracles = ctypes.cdll.LoadLibrary(get_library_path())
