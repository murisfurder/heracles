===============
Data structures
===============

.. automodule:: heracles.tree

-----
Trees
-----

Heracles stores parsed data in trees and can be of two different
classes:

.. autoclass:: heracles.tree.Tree
    :members:
    :special-members: __iter__, __getitem__, __setitem__, __len__, __contains__


.. autoclass:: heracles.tree.ListTree
    :members:
    :special-members: __getitem__,__setitem__,__iter__,__len__,__contains__


-----
Nodes
-----

To store each branch of the tree Heracles uses node objects:

.. autoclass:: heracles.tree.TreeNode
    :members:

.. autoclass:: heracles.tree.ListTreeNode
    :members:

--------------------
LabelNodeList object
--------------------

As the augeas tree structure allows multiple nodes with the same
label a class to manage them it is required.

To allow the common case of an unique label, the instance behaves like
a node implementing label, value getters and setters to access the single
node. In case of multiple nodes it raises. 
:class:`heracles.exceptions.HeraclesTreeLabelError`

.. autoclass:: heracles.tree.LabelNodeList
    :members:

-------------------
Auxiliary functions
-------------------

.. autofunction:: check_list_nodes

.. autofunction:: get_tree_from_nodes

.. autofunction:: get_node

.. rubric:: Footnotes

.. [#f1] by *tree level* and *subtree level* I mean the nodes that share the 
    same parent.

