from os import chmod
from stat import S_IRWXU
from setuptools import setup, find_packages
from setuptools.command.install import install
from distutils.errors import CompileError
from subprocess import call


class new_install(install):

    def run(self):
        install.run(self)
        # set executable to install-libheracles
        chmod('install_libheracles', S_IRWXU)

        options = [self.root] if self.root is not None else []
        v =  call(['./install_libheracles'] + options)
        if v != 0:
            raise CompileError("Unable to compile and install libheracles")
        install.run(self)

setup(name="heracles",
      version="0.0.3",
      author="Jorge Monforte",
      author_email="jorge.monforte@gmail.com",
      packages=find_packages(exclude=["test"]),
      test_suite = "heracles.test.test",
      cmdclass={'install':new_install})
      
