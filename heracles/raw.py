from ctypes import pointer
from heracles.structs import struct_tree_p, struct_tree
from heracles.tree import get_tree_from_nodes, get_node
from heracles.libs import libheracles

def get_raw_tree_from_tree(tree):
    return ManagedRawTree.build_from_tree(tree)

class BaseRawTree(object):
    def __init__(self, first, lens=None):
        assert(isinstance(first, struct_tree_p))
        self.first = first
        self.lens = lens

    def build_tree(self):
        nodes = self._get_nodes(self.first)
        return get_tree_from_nodes(nodes, lens=self.lens)

    def _get_nodes(self, first_p, parent=None):
        assert(isinstance(first_p, struct_tree_p))
        result = []
        raw_node_p = first_p
        while raw_node_p:
            raw_node = raw_node_p.contents
            if raw_node.children:
                children = self._get_nodes(raw_node.children)
            else:
                children = []
            label = raw_node.label
            value = raw_node.value
            node = get_node(children, label=label, value=value, parent=parent) 
            result.append(node)
            raw_node_p = raw_node.next
        return result

class UnmanagedRawTree(BaseRawTree):
    def __del__(self):
        if self.first:
            libheracles.free_tree_node(self.first)

class ManagedRawTree(BaseRawTree):
    @classmethod
    def build_from_tree(cls, tree):
        first = cls.build_raw_nodes(tree._nodes)
        return cls(first)
        
    @classmethod
    def build_raw_nodes(cls, nodes):
        if not nodes:
            return None
        first = None
        previous = None
        for node in nodes:
            raw_node = cls.build_raw_node(node)
            raw_node_p = pointer(raw_node)
            if first is None:
                first = raw_node_p
            if previous is not None:
                previous.next = raw_node_p
            previous = raw_node
        return first

    @classmethod
    def build_raw_node(cls, node):
        raw_node = struct_tree()
        raw_node.label = node.label
        raw_node.value = node.value
        raw_node.next = None
        raw_node.children = cls.build_raw_nodes(node.children._nodes)
        return raw_node


