==============
Parser objects
==============

.. automodule:: heracles.base

--------------------
Heracles main object
--------------------

This is the base class of the Heracles package. It is recomended
to be instantiated once for app as it is pretty memory hungry as it
loads all the lenses at the beginning and it takes its time doing it.

.. autoclass:: Heracles
    :members: 

Lens descriptor
^^^^^^^^^^^^^^^

.. autoclass:: HeraclesLensesDescriptor
    :special-members:


------------------
Lens parser object
------------------

Lens objects can be obtained by its name or the path of the file you
want to parse. One instantiated, the parser instance comes with two 
methods, *get* and *put*. 

* The :meth:`Lens.get` methods reads the text file and creates a python data 
  structure with its contents. 

* The :meth:`Lens.put` method allows regenerating the file with from the python 
  data structure, allowing to recover discarded information in the original 
  parse of the file if its contents are provided in the optional keyword
  parameter *text*.

.. autoclass:: Lens
    :members:
