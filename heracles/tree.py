from heracles.exceptions import HeraclesTreeLabelError, HeraclesListTreeError, HeraclesTreeError
from heracles.util import check_int, str_tree

def check_list_nodes(nodes):
    """Utility function that detects if nodes can be propertly managed
    by a ListTree object"""
    value = 1
    for n in nodes:
        try:
            l = int(n.label)
            if l == value:
                value += 1
            else:
                return False
        except:
            pass
    return False if value == 1 else True

def get_tree_from_nodes(nodes, lens=None):
    """
    Function that selects the best kind of tree object to manage
    some nodes. This function is intended to build the root tree
    
    """
    if check_list_nodes(nodes):
        return ListTree(parent=None, nodes=nodes, lens=lens)
    else:
        return Tree(parent=None, nodes=nodes, lens=lens)

def get_node(children, label="", value="", parent=None):
    """
    Given a sequence of children nodes returns the right parent instance
    to handle them
    
    """
    assert(isinstance(children, list))
    node_class = ListTreeNode if check_list_nodes(children) else TreeNode
    return node_class(label=label, value=value, parent=parent, children=children)

class Tree(object):
    """
    The basic object to store data returned from the lens parser. A ``Tree`` 
    object stores a list of ``TreeNode`` and provides several methods to manage
    them using standar python syntax.

    Tree nodes behave someways like ``dict`` objects but as the augeas parser 
    data structure allow multiple objects with the same label, when accessing 
    them through the container syntax instead of returning a single object, it
    returns a ``LabelNodeList`` instance, which is basically an object to manage
    the sequence of objects with the same label.

    The ``Tree`` objects and their subclasses are also used to handle the 
    children of the ``TreeNode`` instances.

    """

    @classmethod
    def build_from_parent(cls, parent, nodes, default_node_class):
        return cls(parent=parent, nodes=nodes, 
                default_node_class=default_node_class)  

    def __init__(self, parent=None, nodes=None, lens=None, path=None,
            default_node_class=None):
        """
        Instantiates ``Tree`` object.

        Kwargs:
            ``parent`` (TreeNode) : If it is a children tree, the parent node.
            ``nodes`` (list of TreeNode) : The list of nodes that the tree 
                manages
            ``lens`` (Lens) : If it is a master tree, it stores the lens object
                to allow the ``put`` method to render back the text file.
            ``path`` (str) : If it is a master tree, it stores the path of the
                parsed file to allow the ``save`` method to store the changes.
            ``default_node_class`` : (TreeNode class) The default node class
                to be used when creating automaticaly new nodes.

        Examples:
            Create a Tree object:
            >>> t = Tree()

            Add a new node to the tree:
            >>> t.add_new_node(label="new_node", value="value")

            Get the first node of the tree:
            >>> t[0]
            <TreeNode label:'new_node' value:'value' children:0>

            Get the LabelNodeList instance of nodes with label 'new_node':
            >>> t['new_node']
            <LabelNodeList label:'new_node' values:'value'>

            Get the first node of the LabelNodeList:
            >>> t['new_node'][0]
            <TreeNode label:'new_node' value:'value' children:0>

        """
        
        assert(isinstance(parent, TreeNode) or parent is None)
        self.parent = parent
        self.lens = lens
        self.path = path
        self._nodes = nodes if nodes is not None else []
        self.default_node_class = TreeNode if default_node_class is None else default_node_class

    def insert(self, index, node):
        """
        Insert ``node`` into ``index`` place.

        """
        assert(isinstance(node, TreeNode))
        node.parent = self.parent
        self._nodes.insert(index, node)

    def append(self, node):
        """
        Appends ``node`` to tree.

        """
        assert(isinstance(node, TreeNode))
        node.parent = self.parent
        self._nodes.append(node)

    def has_key(self, name):
        """
        Checks if the tree has any node with label ``name``.

        """
        assert(isinstance(name, str) or isinstance(name, int))
        if isinstance(name, int):
            name = str(name)
        for item in self._nodes:
            if item.label == name:
                return True
        return False

    def index(self, node):
        """
        If the tree stores ``node`` returns its position in the tree.

        """
        assert(isinstance(node, TreeNode))
        if not node in self._nodes:
            raise ValueError('Node not in tree')
        return self._nodes.index(node)

    def remove(self, node):
        """
        If the tree stores ``node`` removes the node from the tree.

        """
        assert(isinstance(node, TreeNode))
        if not node in self._nodes:
            raise ValueError("%s not in %s" % (str(node), str(self)))
        self._nodes.remove(node)

    def add_new_node(self, label="", value="", node_class=None):
        """
        Appends a new node with the given ``label`` and ``value``. If not
        ``node_class`` is given it uses the tree's ``default_node_class``.

        """
        if node_class is None:
            node_class = self.default_node_class
        node = node_class(label=label, value=value)
        self.append(node)

    def insert_new_node(self, index, label="", value="", node_class=None):
        """
        Inserts a new node with the given ``label`` and ``value`` in the 
        position given by ``index``. If not ``node_class`` is given it uses the
        tree's ``default_node_class``.

        """
        if node_class is None:
            node_class = self.default_node_class
        node = node_class(label=label, value=value)
        self.insert(index, node)

    def add_new_list_node(self, label="", value=""):
        """
        Appends a new ``ListTreeNode`` instance with the given ``label`` and 
        ``value``. 

        """
        self.add_new_node(label=label, value=value, node_class=ListTreeNode)

    def insert_new_list_node(self, index, label="", value=""):
        """
        Inserts a new ``ListTreeNode`` instance with the given ``label`` and 
        ``value`` in the position given by ``index``. 

        """
        self.insert_new_node(index, label=label, value=value, 
                node_class=ListTreeNode)

    # Lens methods

    def put(self, text=""):
        """
        If it is a master node it renders back to text applying the lens parser.

        If ``text`` is given it uses it to merge with the data of the tree.

        """
        if self.lens is None:
            raise HeraclesTreeError("Unable to put. This tree has no lens")
        return self.lens.put(self, text)

    def save(self, text=""):
        """
        If it is a master node it renders back to text applying the lens parser
        and saves the result to the file in ``path``.

        If ``text`` is given it uses it to merge with the data of the tree.

        """
        if self.path is None:
            raise HeraclesTreeError("Unable to dump to a file withot a given path")
        dump = self.put(text)
        with open(self.path, "w") as f:
            f.write(dump)

    # Special methods

    def __iter__(self):
        for node in self._nodes:
            yield node

    def __getitem__(self, name):
        if isinstance(name, basestring):
            return LabelNodeList.build(self, name)
        elif isinstance(name, int):
            return self._get_item_by_integer(name)
        else:
            raise KeyError("Unsupported key type '%s'" % str(type(name)))

    def __delitem__(self, item):
        self.remove(item)

    def __setitem__(self, name, value):
        assert(isinstance(value, str) or isinstance(value, TreeNode))
        assert(isinstance(name, str) or isinstance(name, int))
        if isinstance(name, str):
            if isinstance(value, str):
                value = self.default_node_class(label=name, value=value, 
                        parent=self.parent)
            elif isinstance(value, TreeNode):
                value.label = name
                value.parent = self.parent
            self._nodes.append(value)
        elif isinstance(name, int):
            self._set_item_by_integer(name, value)

    def _check_index(self, index):
        l = len(self)
        if index < 0:
            index = l + index
        return 0 <= index < l 

    def _get_item_by_integer(self, index):
        if not self._check_index(index):
            raise IndexError("Tree index out of range")
        return self._nodes[index]

    def _set_item_by_integer(self, index, value):
        if not self._check_index(index):
            raise IndexError("Tree assignment out of range")
        if isinstance(value, str):
            self[index].value = value
        elif isinstance(value, TreeNode):
            value.tree = self
            self._nodes[index] = value

    def __str__(self):
        return str_tree(self)

    def __repr__(self):
        return "<%s nodes:%s>" % (self.__class__.__name__,",".join(map(str, self._nodes)))

    def __contains__(self, value):
        if isinstance(value, TreeNode):
            return value in self._nodes
        elif isinstance(value, str):
            for n in self._nodes:
                if n.label == value:
                    return True
            return False
        else:
            raise HeraclesTreeError('Unsupported type')

    def __len__(self):
        return len(self._nodes)

    def serialize(self):
        res = []
        for item in self:
            res.append(item.serialize())
        return res

class ListTree(Tree):
    """
    This is a subclass of ``Tree`` to handle list of nodes wich uses
    counter as label, so it can be handled like a regular python ``list``
    object.

    """
    # index : As it works in getitem set item.
    # raw_index : The self._nodes node intex
    # label_index : The index as it is stored in node.label

    def insert(self, index, tree_node):
        """
        Insert ``node`` into ``index`` place.

        """
        assert(isinstance(tree_node, TreeNode)) 
        assert(isinstance(index, int))
        label_index = index + 1
        tree_node.label = str(label_index)
        raw_index = self._get_raw_index(index)
        super(ListTree, self).insert(raw_index, tree_node)
        self._update_index(label_index + 1, +1)

    def append(self, tree_node):
        """
        Appends ``node`` to tree.

        """
        assert(isinstance(tree_node, TreeNode))
        last_index = len(self)
        tree_node.label = str(last_index + 1)
        super(ListTree, self).append(tree_node)

    def index(self, tree_node):
        """
        If the tree stores ``node`` returns its position in the tree.

        """
        assert(isinstance(tree_node, TreeNode))
        if tree_node in self:
            try:
                label_index = int(tree_node.label)
                return label_index - 1
            except ValueError:
                raise HeraclesListTreeError('TreeNode is not an indexed node')
        else:
            raise ValueError('Node not in tree')

    def remove(self, tree_node):
        """
        If the tree stores ``node`` removes the node from the tree.

        """
        assert(isinstance(tree_node, TreeNode))
        super(ListTree, self).remove(tree_node)
        try:
            label_index = int(tree_node.label)
            index = label_index - 1
            self._update_index(index, -1)
        except ValueError:
            pass

    def add_new_node(self, value, node_class=None):
        """
        Appends a new node with the given ``label`` and ``value``. If not
        ``node_class`` is given it uses the tree's ``default_node_class``.

        """
        if node_class is None:
            node_class = self.default_node_class
        node = node_class(value=value)
        self.append(node)

    def insert_new_node(self, index, value, node_class=None):
        """
        Inserts a new node with the given ``label`` and ``value`` in the 
        position given by ``index``. If not ``node_class`` is given it uses the
        tree's ``default_node_class``.
        
        """
        if node_class is None:
            node_class = self.default_node_class
        node = node_class(value=value)
        self.insert(index, node)

    def add_new_list_node(self, value):
        """
        Appends a new ``ListTreeNode`` instance with the given ``label`` and 
        ``value``. 

        """
        self.add_new_node(value, node_class=ListTreeNode)

    def insert_new_list_node(self, index, value):
        """
        Inserts a new ``ListTreeNode`` instance with the given ``label`` and 
        ``value`` in the position given by ``index``. 

        """
        self.insert_new_node(index, value, node_class=ListTreeNode)

    def _get_raw_index(self, index):
        l = len(self)
        if index < 0:
            index = l + index
        if not 0 <= index < l:
            raise IndexError('Index out of range')
        for i, node in enumerate(self._nodes):
            try:
                label_index = int(node.label)
                if label_index - 1 == index:
                    return i
            except ValueError:
                pass

    def _update_index(self, from_index, value):
        """Updates labels of the next items to keep sequentiality"""
        from_label_index = from_index + 1
        for item in self:
            label = int(item.label)
            if label >= from_label_index:
                item.label = str(label + value)

    def _get_item_by_integer(self, index):
        raw_index = self._get_raw_index(index)
        return self._nodes[raw_index]

    def _set_item_by_integer(self, index, value):
        raw_index = self._get_raw_index(index)
        if isinstance(value, str):
            self._nodes[raw_index].value = value
        elif isinstance(value, TreeNode):
            value.parent = self.parent
            self._nodes[raw_index] = value

    def __contains__(self, value):
        assert(isinstance(value, str) or isinstance(value, TreeNode))
        if isinstance(value, TreeNode):
            return value in self._nodes
        for n in self:
            if n.value == value:
                return True
        return False

    def __iter__(self):
        for child in self._nodes:
            if check_int(child.label): 
                yield child

    def __len__(self):
        i = 0
        for node in self:
            i += 1
        return i

class TreeNode(object):
    """
    Basic storage unit of Heracles. Each ``Tree`` contains a list of 
    ``TreeNode`` instance and of its subclasses.

    ``TreeNode`` stores its children in a ``Tree`` instance.
    """
    children_class = Tree

    def __init__(self, label="", value="", parent=None, children=None, 
            default_children_class=None):
        """
        ``TreeNode`` contains:
            ``label`` (str) : A value that classifies the node.
            ``value`` (str) : The value stored in the node.
            ``parent`` (TreeNode) : If it is a children node, its parent.
            ``children`` (list of TreeNode) : The list of nodes that are its
                children.

        Also you can provide the node with the ``default_children_class`` that 
        can be used to automatic instantiate them.


        """
        assert(isinstance(label, str) or label is None)
        assert(isinstance(value, str) or value is None)
        assert(isinstance(parent, TreeNode) or parent is None)
        self.parent = parent
        self.label = label
        self.value = value
        children = [] if children is None else children
        self.children = self.children_class.build_from_parent(self, children,
                default_children_class)

    def serialize(self):
        res = {}
        res['label'] = self.label
        res['value'] = self.value
        res['children'] = self.children.serialize()
        return res

    def __repr__(self):
        return "<%s label:'%s' value:'%s' children:%d>" % (self.__class__.__name__,
                self.label, self.value, len(self.children))

class ListTreeNode(TreeNode):
    """
    ``TreeNode`` stores its children in a ``Tree`` instance.

    """
    children_class = ListTree

class LabelNodeList(object):
    """
    ``LabelNodeList`` is a helper class that allows access to several nodes with
    the same name.

    Nodes can be accessed with a mixture of dict and list methods, so you can 
    get the container methods to access numerically returning or setting
    according to the order in the list, or by an string key that represents
    the value of the node.

    If there is a single node in the list you can use the ``value`` and
    ``children`` of the ``LabelNodeList`` instance to access its contents.


    """
    @classmethod
    def build(cls, tree, label):
        """
        Checks if there are nodes with ``label`` in ``tree`` before 
        instantiating.

        """
        i = 0
        for item in tree._nodes:
            if item.label == label:
                i += 1
        if i == 0:
            raise KeyError("Unable to find item '%s'" % label)
        else:
            return cls(tree, label)

    def __init__(self, tree, label):
        self.tree = tree
        self.label = label

    # Masked methods used to access node properties in case there
    # is just one node to simplify syntax

    def _test_single_node_label(self):
        if len(self) != 1:
            raise HeraclesTreeLabelError("Single node label methods only accesible with one node")

    @property
    def value(self):
        """
        If there is a single node in the list returns its ``value``.

        """
        self._test_single_node_label()
        return self[0].value

    @value.setter
    def value(self, value):
        """
        If there is a single node in the list sets its ``value``.

        """
        self._test_single_node_label()
        self[0].value = value

    @property
    def children(self):
        """
        If there is a single node in the list returns its ``children``.

        """
        self._test_single_node_label()
        return self[0].children

    @property
    def parent(self):
        """
        Returns the parent of the tree instance.

        """
        return self.tree.parent

    # Common list methods
    def insert(self, index, item):
        """
        Insert ``node`` into ``index`` place, the order is keept inside the 
        tree.

        """
        assert(isinstance(index, int))
        assert(isinstance(item, str) or isinstance(item, TreeNode))
        if isinstance(item, str):
            item = self.tree.default_node_class(value=item, label=self.label) 
        else:
            item.label = self.label
        l = len(self)
        if index < 0:
            index = l - index
        if index < 0:
            index = 0
        if index >= l:
            self.append(item)
        else:
            t_item = self[index]
            t_index = self.tree.index(t_item)
            self.tree.insert(t_index, item)

    def remove(self, item):
        """
        If the tree stores ``node`` removes the node from the tree.

        """
        if not item in self:
            raise ValueError("Node not in list")
        self.tree.remove(item)

    def append(self, item):
        """
        Adds a node to the tree setting its label to the LabelNodeList label

        """
        assert(isinstance(item, str) or isinstance(item, TreeNode))
        if isinstance(item, str):
            item = self.tree.default_node_class(value=item, label=self.label) 
        else:
            item.label = self.label
        self.tree.append(item)

    def __iter__(self):
        for item in self.tree._nodes:
            if item.label == self.label:
                yield item

    def __getitem__(self, index):
        assert(isinstance(index, int) or isinstance(index, str))
        if isinstance(index, int):
            l = len(self)
            if index < 0:
                index = l + index
            if not 0 <= index < l:
                raise IndexError("Index out of range")
            for i, item in enumerate(self):
                if i == index:
                    return item
        elif isinstance(index, str):
            for node in self:
                if node.value == index:
                    return node
            raise ValueError("Node not in list")
        else:
            raise HeraclesTreeLabelError("Un supported index type")

    def __setitem__(self, index, value):
        assert(isinstance(value, str) or isinstance(value, TreeNode))
        item = self[index]
        if isinstance(value, str):
            item.value = value
        elif isinstance(value, TreeNode):
            value.label = self.label
            tree_index = item.index
            self.tree.remove(item)
            self.tree.insert(tree_index, item)

    def __delitem__(self, item):
        self.remove(item)

    def __contains__(self, item):
        for x in self:
            if x == item:
                return True
        return False

    def __len__(self):
        for i, item in enumerate(self):
            pass
        return i + 1

    def __repr__(self):
        return "<%s label:'%s' values:%s>" % (self.__class__.__name__,
                self.label, ",".join(map(lambda x:"'%s'" % x.value, self)))

    def __str__(self):
        if len > 1:
            raise HeraclesTreeLabelError('Cannot return the value from a label with multiple values')
        if len == 0:
            raise HeraclesTreeLabelError('Cannot return the value from an empty label')
        return self[0].value


