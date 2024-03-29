import os
import sys

# Disable loading of dynamic link libraries
if sys.argv[1] != 'test':
    os.environ['HERACLES_DISABLE_LIBHERACLES'] = "1"

from os import chmod
from stat import S_IRWXU
from setuptools import setup, find_packages
from distutils.cmd import Command
from distutils.errors import CompileError
from distutils.command.build import build
from subprocess import call
from heracles import __version__

LIBDIR = "lib"
#ORIGIN_FILE = 
LIBRARY_NAME = "libheracles"

class build_libheracles(Command):
    user_options = [
            ('inplace', 'i',
             'ignore build-lib and put compiler extensions into the source' +
             'directory alongsie your pure python modules'),
            ('build-lib=', 'b',
             "directory for compiled extension modules"),
            ]
    boolean_options = ['inplace']

    def initialize_options(self):
        self.inplace = 0
        self.build_lib = None
        self.plat_name = None

    def finalize_options(self):
        self.set_undefined_options('build', 
                ('build_lib', 'build_lib'),
                ('plat_name', 'plat_name'))

    def run(self):
        self.compile()

    def compile(self):
        # set executable to install-libheracles
        chmod('build_libheracles', S_IRWXU)
        
        v =  call(['./build_libheracles', self.get_dest_dir()] )
        if v != 0:
            raise CompileError("Unable to compile libheracles")

    def get_dest_dir(self):
        if self.inplace:
            dest_dir = os.path.join('heracles')
        else:
            dest_dir = os.path.join(self.build_lib, 'heracles')
        return dest_dir

class new_build(build):
    sub_commands = build.sub_commands + [('build_libheracles', lambda x:True)]

setup(name="heracles",
      version=__version__,
      author="Jorge Monforte",
      author_email="jorge.monforte@gmail.com",
      description="A configuration file parser",
      packages=find_packages(exclude=["test"]),
      package_data={"heracles.test":["data/*"]},
      test_suite = "heracles.test.test",
      cmdclass={'build':new_build, "build_libheracles":build_libheracles})
      
