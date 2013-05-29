A Python lens configuration file parser.

It uses `libheracles <https://github.com/llou/libheracles>`_  to parse files 
into Python objects.

------
Status
------

Heracles is now in **alpha**, so you can play with it but it's use in production
is completely discouraged.

I have tested it on Python 2.6 and 2.7 running in Debian and MacOs. It should
work also with 2.5 but I haven't tested yet.

----------
Installing
----------

To install it from repository::

    $ git clone https://github.com/llou/heracles.git
    $ cd heracles
    $ sudo python setup.py install

Should make the thing work.

I have uploaded it to *PIP*, so the easiest way to get it working is through::

    $ sudo pip install heracles

-------
Testing
-------

To test if heracles runs in your computer before installing you have to build 
``libheracles`` first::

    $ python setup.py build_libheracles --inplace

Then you can run the test suites by::

    $ python setup.py test
  
-----------
Lens parser
-----------

A lens parser is a kind of parser developed for the 
`Armony Project <https://alliance.seas.upenn.edu/~harmony/>`_ with 
the idea to parse a file modify the extracted data and regenerate the file from 
the data without destroying other information like comments stored in the 
original file.

A len parser normally works with two methods *get* and *put*, the first parses
the file creating a tree structure easily modifiable with any program, then the
*put* method regenerates the file with the modifications keeping the data 
discarded in the *get* parse because it simultaneously parses the original file
at the same time it regenerates the modified one.

------------
How it works
------------

First of all you have to instantiate an *Heracles* object::
    >>> from heracles import Heracles
    >>> h = Heracles()

This should load all the default lenses. Now if you want to load a 
lens parser you have two ways of doing it:

* If you know the lens name:::

        >>> l = h.lenses['Aptsources']

* Given the file you want to parse:::

        >>> l = h.get_lens_by_path('/etc/apt/sources.list')


Now with the lens parser loaded you can start parsing:::

    >>> text = file('/etc/apt/sources.list').read()
    >>> print text
    deb http://ftp.es.debian.org/debian/ squeeze main contrib non-free
    ...
    >>> t = l.get(text)

You get a *ListTree* object, that you can modify the values using 
standar Python methods. ListTree objects behave in some ways like *list*
of *TreeNode* objects. 

A *ListTree* is returned when heracles detects some *TreeNode* labels
are correlative numbers starting at 1. This allows straight access to 
**indexed** nodes using standar Python syntax. For example lets get the first 
**indexed** entry of the configuration file:::

    >>> e = t[0]
    >>> print e
    <Heracles.TreeNode label:'1' value:'' children:6>

TreeNodes have three main properties, *label* and *value* are strings 
and *children* can be a *Tree* or a *ListTree* object. If you look close you will 
see the entry has 6 children, each one is a different TreeNode with its *label*
, *value* and *children*. ::

    >>> c = e.children
    >>> for n in c: print n
    <Heracles.TreeNode label:'type' value:'deb' children:0>
    <Heracles.TreeNode label:'uri' value:'http://ftp.es.debian.org/debian/' children:0>
    <Heracles.TreeNode label:'distribution' value:'squeeze' children:0>
    <Heracles.TreeNode label:'component' value:'main' children:0>
    <Heracles.TreeNode label:'component' value:'contrib' children:0>
    <Heracles.TreeNode label:'component' value:'non-free' children:0>

In this case *e.children* is *Tree* objects instead of a *ListTree*.
*Tree* objects behave someways like *dicts*, you can access TreeNodes by their
label.::

    >>> print c['type'].value
    'deb'

There is a caveat working with trees as dicts due the support of multiple
items with the same label. In this case heracles returns an iterable with
all nodes with this label.::

    >>> for i in c['component']: print i
    <Heracles.TreeNode label:'component' value:'main' children:0>
    <Heracles.TreeNode label:'component' value:'contrib' children:0>
    <Heracles.TreeNode label:'component' value:'non-free' children:0>

To select which node you use it's index:::

    >>> n = c['component'][2]
    >>> print n.value
    'non-free'

*Tree* objects also allow straight access through the index of the node.
So if you want to get the first children:::

    >>> print c[0]
    <Heracles.TreeNode label:'type' value:'deb' children:0>

You can modify the tree using standar methods.::

    >>> c.remove(n)
    >>> for i in c['component']: print i
    <Heracles.TreeNode label:'component' value:'main' children:0>
    <Heracles.TreeNode label:'component' value:'contrib' children:0>

If you want to set values through it's label you have to remember
to set the index of list of nodes with that label:::

    >>> c['uri'][0] = 'http://ftp.uk.debian.org/debian/'
    >>> for n in c: print n
    <Heracles.TreeNode label:'type' value:'deb' children:0>
    <Heracles.TreeNode label:'uri' value:'http://ftp.uk.debian.org/debian/' children:0>
    <Heracles.TreeNode label:'distribution' value:'squeeze' children:0>
    <Heracles.TreeNode label:'component' value:'main' children:0>
    <Heracles.TreeNode label:'component' value:'contrib' children:0>

Now with the updated tree object we can regenerate the file.::

    >>> text = l.put(t, '')
    >>> print text
    deb http://ftp.uk.debian.org/debian/ squeeze main contrib
    ...

As you can see it updated the file.

-----
About
-----

Heracles is developed by Jorge Monforte <jorge.monforte@gmail.com> to provide
its remote compute automation tool of a configuration file parser.

Copyright 2013 Jorge Monforte. Distributed under the LGPL license.

