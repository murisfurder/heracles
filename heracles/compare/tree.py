from heracles.tree import Tree, ListTree, TreeNode, ListTreeNode
from heracles.zss.simple_tree import Node

# TODO Reset de label values to "" in ListTrees

def check_int(value):
    if isinstance(value, int):
        return True
    elif isinstance(value, basestring):
        for x in value:
            if not x in "0123456789":
                return False
        return True
    else:
        return False

def build_root_from_tree(tree, ignore_comments=True):
    # TODO Add ignore comments
    root = Node(label="root")
    for child in tree:
        n = build_node_from_tree_node(child)
        root.addkid(n)
    return root

def build_node_from_tree_node(tree_node):
    node = Node(label=tree_node.label, value=tree_node.value)
    for child in tree_node.children:
        n = build_node_from_tree_node(child)
        node.addkid(n)
    return node

def build_tree_from_root(root_node):
    tree_type = get_tree_type_from_node(root_node)
    tree = tree_type()
    for node in root_node.children:
        tree_node = build_tree_node_from_node(node)
        tree.children.append(tree_node)
    return tree

def build_tree_node_from_node(node):
        node_type = get_node_type_from_node(node)
        tree_node = node_type(label=node.label, value=node.value)
        for child in node.children:
            c_node = build_tree_node_from_node(child)
            tree_node.children.append(c_node)

def check_children_listable(node):
    for c in node.children:
        if not ( c.label == "" or check_int(c.label)):
            return False
    return True

def get_tree_type_from_node(node):
    if check_children_listable(node):
        return ListTree
    else:
        return Tree

def get_node_type_from_node(node):
    if check_children_listable(node):
        return ListTreeNode
    else:
        return TreeNode

