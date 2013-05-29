import os
from platform import system
import ctypes
import ctypes.util
from heracles.util import get_heracles_path
from heracles.exceptions import HeraclesError

LIBRARY_NAME = "libheracles"
LIBRARY_DIR = "libs"
ENV_DISABLE = 'HERACLES_DISABLE_LIBHERACLES'

disabled_lib = ENV_DISABLE in os.environ and os.environ[ENV_DISABLE] == "1"

def get_library_name():
    s = system()
    if s == "Linux":
        ext = "so"
    elif s == "Darwin":
        ext = "dylib"
    elif s == "nt":
        ext = "dll"
    else:
        raise HeraclesError("Unknown operating system")
    return LIBRARY_NAME + "." + ext

def get_library_path():
    h_path = get_heracles_path()
    library_name = get_library_name()
    return os.path.join(h_path, LIBRARY_DIR, library_name)

if not disabled_lib:
    libheracles = ctypes.cdll.LoadLibrary(get_library_path())
else:
    print "Warning disabling libheracles. Heracles wont work."
    libheracles = None

