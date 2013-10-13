from unittest import TestCase
from itertools import permutations
from zss.simple_tree import Node, SetNode, NodeTreesGenerator

class SetNoteTestCase(TestCase):
    def test_set_node(self):
        n = (
            SetNode("test")
                .addkid(Node("test1"))
                .addkid(Node("test2"))
                )
        self.assertTrue(isinstance(n, SetNode))
        self.assertEqual(len(n.children), 2)

    def test_iter_set_nodes(self):
        n = (
             SetNode("snode1")
                 .addkid(SetNode("snode2")
                     .addkid(Node("node1"))
                     .addkid(SetNode("snode3"))
                     )
                 .addkid(Node("node1")
                     .addkid(SetNode("snode4"))
                     .addkid(Node("node3"))
                     )
                 )
        labels = set([ x.label for x in n.iter_set_nodes() ])
        test_labels = set([ "snode%d" %i for i in range(1,5) ])

        self.assertEqual(labels, test_labels)

def tree_compare(A, B):
    try:
        node_pairs = zip(A.iter(), B.iter())
    except:
        raise Exception("Comparing trees with different sizes")
    for a, b in node_pairs:
        if a != b:
            return False
    return True

def compare_lists_of_trees(l1, l2):
    try:
        tree_pairs = zip(l1, l2)
    except:
        raise Exception("Comparing lists of different sizes")
    for a, b in tree_pairs:
        if not tree_compare(a,b):
            return False
    return True


def tree_in_trees(tree, trees):
    for tree2 in trees:
        if compare_lists_of_trees(tree, tree2):
            return True
    return False

class NodeTreeGeneratorTestCase(TestCase):
    def assert_trees_equal(self, l1, l2):
        for p in permutations(l1):
            if compare_lists_of_trees(p, l2):
                return 
        self.fail("Trees are different")

    def test_basic(self):
        o = (
             SetNode("a")
                .addkid(Node("b"))
                .addkid(Node("c"))
                )

        s = [(
                Node("a")
                    .addkid(Node("b"))
                    .addkid(Node("c"))
                    ),
             (
                Node("a")
                    .addkid(Node("c"))
                    .addkid(Node("b"))
                    )
             ]
        self.assert_trees_equal(list(NodeTreesGenerator(o)), s)

    def test_multiple(self):
        o = (SetNode("a")
                .addkid(SetNode("b")
                    .addkid(Node("e"))
                    .addkid(Node("f"))
                        )
                .addkid(Node("c"))
                )

        s = [(Node("a")
                .addkid(Node("b")
                    .addkid(Node("e"))
                    .addkid(Node("f"))
                    )
                .addkid(Node("c"))
                ),
             (Node("a")
                .addkid(Node("b")
                    .addkid(Node("f"))
                    .addkid(Node("e"))
                    )
                .addkid(Node("c"))
                ),
             (Node("a")
                .addkid(Node("c"))
                .addkid(Node("b")
                    .addkid(Node("e"))
                    .addkid(Node("f"))
                    )
                ),
             (Node("a")
                .addkid(Node("c"))
                .addkid(Node("b")
                    .addkid(Node("f"))
                    .addkid(Node("e"))
                    )
                )
             ]
        self.assert_trees_equal(list(NodeTreesGenerator(o)), s)







                




