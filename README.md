Heracles
========

A python lens configuration file parser.

It uses [libheracles](https://github.com/llou/libheracles) that is a fork of the 
augeas project to parse files into python objects.

Status
------

Heracles is now in **alpha**, so you can play with it but it's use in production
is completely discouraged.

Installing
----------

It comes bundled with the libheracles installer so running *sudo 
python setup.py install* should make the thing work.

I have uploaded it to PIP, so the easiest way to get it working
is through *sudo pip install heracles*.

How it works
------------

First of all you have to instantite an *Heracles* object
```
>>> from heracles import Heracles
>>> h = Heracles()
```

This should load all the default lenses. Now if you want to load a 
lens parser you have two ways of doing it:

* If you know the lens name:

        `>>> l = h.lenses['Aptsources']`

* Given the file you want to parse:

        `>>> l = h.get_lens_by_path('/etc/apt/sources.list')`

Now with the lens parser loaded you can start parsing:

```
>>> text = file('/etc/apt/sources.list').read()
>>> print text
deb http://ftp.es.debian.org/debian/ squeeze main contrib non-free
...
>>> t = l.get(text)
```

You get a tree object, that you can modify the values using 
standar python methods. Tree objects behave in some ways like *list*.
For example lets get the first entry of the configuration file:

```
>>> e = t[0]
>>> print e
<Heracles.TreeNode label:'1' value:'' children:6>
```

If you look close you will see the entry has 6 children, children
are tree nodes stored in a Tree object. *Tree* objects behave also like 
*dicts*.

```
>>> c = e.children
>>> print c['type'].value
'deb'
```

There is a caveat working with trees as dicts due the support of multiple
items with the same label. In this case heracles returns an iterable with
all nodes with this label.

```
>>> for i in c['component']: print i
<Heracles.TreeNode label:'component' value:'main' children:0>
<Heracles.TreeNode label:'component' value:'contrib' children:0>
<Heracles.TreeNode label:'component' value:'non-free' children:0>
```

You can also access by index.

```
>>> n = c['component'][2]
>>> print n.value
'non-free'
```

You can modify the tree using standar methods.

```
>>> c.remove(n)
>>> for i in c['component']: print i
<Heracles.TreeNode label:'component' value:'main' children:0>
<Heracles.TreeNode label:'component' value:'contrib' children:0>
```

Now with the updated tree object we can regenerate the file.

```
>>> text = l.put(t, '')
>>> print text
deb http://ftp.es.debian.org/debian/ squeeze main contrib
...
```

As you can see it updated the file.
