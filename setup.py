from setuptools import setup, find_packages
from setuptools.command.install import install
from distutils.errors import CompileError
from subprocess import call


class new_install(install):

    def run(self):
        install.run(self)
        root = self.root if self.root is not None else ""
        v =  call(['./install_libheracles', root])
        if v != 0:
            raise CompileError("Unable to compile and install libheracles")
        install.run(self)

setup(name="heracles",
      version="0.0.1",
      author="Jorge Monforte",
      author_email="jorge.monforte@gmail.com",
      packages=find_packages(exclude=["test"]),
      cmdclass={'install':new_install})
      
