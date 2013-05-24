from heracles.structs import struct_tree_p
from heracles.exceptions import HeraclesTreeLabelError, HeraclesListTreeError
from heracles.util import check_int

class RawTree(object):
    def __init__(self, raw_tree_p):
        self.raw_tree_p = raw_tree_p

    def __iter__(self):
        node_p = self.raw_tree_p
        while True:
            if not node_p:
                break
            yield node_p.contents
            node_p = node_p.contents.next

class LabelNodeList(object):
    @classmethod
    def build(cls, tree, label):
        i = 0
        for item in tree._nodes:
            if item.label == label:
                i += 1
        if i == 0:
            raise KeyError("Unable to find item '%s'" % label)
        else:
            return cls(tree, label)

    # Masked methods used to access node properties in case there
    # is just one node to simplify syntax

    def _test_single_node_label(self):
        if len(self) != 1:
            raise HeraclesTreeLabelError("Single node label methods only accesible with one node")

    @property
    def value(self):
        self._test_single_node_label()
        return self[0].value

    @value.setter
    def value(self, value):
        self._test_single_node_label()
        self[0].value = value

    # Common list methods

    def __init__(self, tree, label):
        self.tree = tree
        self.label = label

    def remove(self, item):
        if not item in self:
            raise ValueError("Node not in list")
        self.tree.remove(item)

    def insert(self, index, item):
        assert(isinstance(index, int))
        assert(isinstance(item, str) or isinstance(item, TreeNode))
        if isinstance(item, str):
            item = TreeNode(self.tree.heracles, value=item, label=self.label, tree=self.tree)
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
            t_index = t_item.index
            self.tree.insert(t_index, item)

    def append(self, item):
        assert(isinstance(item, str) or isinstance(item, TreeNode))
        if isinstance(item, str):
            item = TreeNode(self.tree.heracles, value=item, label=self.label, tree=self.tree)
        else:
            item.label = self.label
        self.tree.append(item)

    def __iter__(self):
        for item in self.tree._nodes:
            if item.label == self.label:
                yield item

    def __getitem__(self, index):
        assert(isinstance(index, int))
        l = len(self)
        if index < 0:
            index = l + index
        if not 0 <= index < l:
            raise IndexError("Index out of range")
        for i, item in enumerate(self):
            if i == index:
                return item

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
        return "<%s values:%s>" % (self.__class__.__name__,
                ",".join(map(lambda x:"'%s'" % x.v, self)))

    def __str__(self):
        if len > 1:
            raise HeraclesTreeLabelError('Cannot return the value from a label with multiple values')
        if len == 0:
            raise HeraclesTreeLabelError('Cannot return the value from an empty label')
        return self[0].value

def get_nodes_from_raw_tree(heracles, first_p, parent=None):
    assert(isinstance(first_p, struct_tree_p))
    result = []
    raw_node_p = first_p
    while raw_node_p:
        raw_node = raw_node_p.contents
        if raw_node.children:
            children = get_nodes_from_raw_tree(heracles, raw_node.children)
        else:
            children = []
        label = raw_node.label.value
        value = raw_node.value.value
        node = TreeNode(heracles, label=label, value=value, parent=parent, 
                children=children)
        result.append(node)
        raw_node_p = raw_node.next
    return result

class Tree(object):
    tree_classes = []
    node_class = None

    @classmethod
    def build_from_raw_tree_pointer(cls, heracles, first):
        nodes = get_nodes_from_raw_tree(first)
        return cls.build(heracles, nodes=nodes)

    @classmethod
    def build_from_parent(cls, parent):
        cls.build(parent.heracles, parent=parent, nodes=parent.nodes)

    @classmethod
    def build(cls, heracles, parent=None, nodes=[]):
        for tc in cls.tree_classes:
            assert(issubclass(tc, cls))
            if tc.check_tree(nodes):
                return tc(heracles, parent=parent, nodes=nodes)
        return cls(heracles=heracles, parent=parent, nodes=nodes)

    @classmethod
    def check_tree(cls, nodes):
        return True
        
    def __init__(self, heracles, parent=None, nodes=[]):
        assert(isinstance(parent, TreeNode) or parent is None)
        self.parent = parent
        self._nodes = nodes

    def insert(self, index, node):
        assert(isinstance(node, TreeNode))
        node.tree = self
        self._nodes.insert(index, node)

    def append(self, node):
        assert(isinstance(node, TreeNode))
        node.tree = self
        self._nodes.append(node)

    def has_key(self, name):
        assert(isinstance(name, str) or isinstance(name, int))
        if isinstance(name, int):
            name = str(name)
        for item in self._nodes:
            if item.label == name:
                return True
        return False

    def remove(self, node):
        assert(isinstance(node, TreeNode))
        if not node in self._nodes:
            raise ValueError("%s not in %s" % (str(node), str(self)))
        self._nodes.remove(node)

    def add_node(self, label="", value=""):
        node = self.node_class(label=label, value=value)
        self._nodes.append(node)

    def insert_node(self, index, label="", value=""):
        node = self.node_class(label=label, value=value)
        self._nodes.insert(index, node)

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
                self._add_child(label=name, value=value)
            elif isinstance(value, TreeNode):
                value.label = name
                self.append(value)
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

    def __repr__(self):
        return "<%s nodes:%s>" % (self.__class__.__name__,",".join(map(str, self._nodes)))

    def __len__(self):
        return len(self._nodes)

    def serialize(self):
        res = []
        for item in self:
            res.append(item.serialize())
        return res

class ListTree(Tree):
    # index : As it works in getitem set item.
    # raw_index : The self._nodes node intex
    # label_index : The index as it is stored in node.label

    def _get_raw_index(self, index):
        l = len(self)
        if index < 0:
            index = l + index
        if not 0 <= index < l:
            raise IndexError('Index out of range')
        for i, node in enumerate(self):
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

    def insert(self, index, tree_node):
        assert(isinstance(tree_node, TreeNode)) 
        assert(isinstance(index, int))
        raw_index = self._get_raw_index(index)
        super(ListTree, self).insert(raw_index, tree_node)
        self._update_index(index + 1, +1)

    def append(self, tree_node):
        assert(isinstance(tree_node, TreeNode))
        last_index = int(self[-1].label)
        tree_node.label = str(last_index + 1)
        super(ListTree, self).append(tree_node)

    def remove(self, tree_node):
        assert(isinstance(tree_node, TreeNode))
        super(ListTree, self).remove(tree_node)
        try:
            label_index = int(tree_node.label)
            index = label_index - 1
            self._update_index(index, -1)
        except ValueError:
            pass

    def index(self, tree_node):
        assert(isinstance(tree_node, TreeNode))
        if tree_node in self:
            try:
                label_index = int(tree_node.label)
                return label_index - 1
            except ValueError:
                raise HeraclesListTreeError('TreeNode is not an indexed node')
        else:
            raise ValueError('Node not in tree')

    def _get_item_by_integer(self, index):
        raw_index = self._get_raw_index(index)
        return super(ListTree, self)._get_item_by_integer(raw_index)

    def _set_item_by_integer(self, index, value):
        raw_index = self._get_raw_index(index)
        return super(ListTree, self)._set_item_by_integer(raw_index, value)

    def __iter__(self):
        for child in self._nodes:
            if check_int(child.label): 
                yield child

    def __len__(self):
        for i, item in enumerate(self):
            pass
        return i+1

# Update Tree object to detect ListTree objects
Tree.tree_classes = [ListTree]

class TreeNode(object):
    def __init__(self, heracles, label=None, value=None, parent=None, children=[]):
        assert(isinstance(label, str) or label is None)
        assert(isinstance(value, str) or value is None)
        assert(isinstance(parent, TreeNode) or parent is None)
        self.heracles = heracles
        self.parent = parent
        if label is not None:
            self.label = label
        if value is not None:
            self.value = value
        self._children = children

    @property
    def children(self):
        return Tree.build(parent=self, nodes=self._children)

    def serialize(self):
        res = {}
        res['label'] = self.label
        res['value'] = self.value
        res['children'] = self.children.serialize()
        return res

    def __repr__(self):
        return "<Heracles.TreeNode label:'%s' value:'%s' children:%d>" % (str(self.label),
                str(self.value), len(self.children))



