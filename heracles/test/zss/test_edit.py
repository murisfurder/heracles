from unittest import TestCase
from zss.edit import EditPathGenerator, INSERT, REMOVE, UPDATE
from zss.simple_tree import Node

class EditPathGeneratorTestCase(TestCase):

    def assert_insert(self, edits, label):
       for e in edits:
           if e[0] == INSERT:
               if e[2].label == label:
                   return
       self.fail("Value '%s' not inserted in tree" % label)

    def assert_remove(self, edits, label):
       for e in edits:
           if e[0] == REMOVE:
               if e[1].label == label:
                   return
       self.fail("Value '%s' not removed in tree" % label)

    def assert_update(self, edits, label1, label2):
       for e in edits:
           if e[0] == UPDATE:
               if e[1].label == label1 and e[2].label == label2:
                   return
       self.fail("Value '%s' not updated in tree" % label1)

    def test_equal(self):
        A = (
            Node("f")
                .addkid(Node("d")
                    .addkid(Node("a"))
                    .addkid(Node("c")
                        .addkid(Node("b"))))
                .addkid(Node("e"))
                )
        B = (
            Node("f")
                .addkid(Node("d")
                    .addkid(Node("a"))
                    .addkid(Node("c")
                        .addkid(Node("b"))))
                .addkid(Node("e"))
                )

        e = EditPathGenerator(A,B)
        self.assertEqual(0, e.get_tree_dist())
        self.assertEqual(len(e.get_tree_edits()), 0)

    def test_insert(self):
        A = (
            Node("f")
                .addkid(Node("d")
                    .addkid(Node("a"))
                    .addkid(Node("c")
                        .addkid(Node("b"))))
                .addkid(Node("e"))
                )
        B = (
            Node("f")
                .addkid(Node("d")
                    .addkid(Node("a"))
                    .addkid(Node("X"))
                    .addkid(Node("c")
                        .addkid(Node("b"))))
                .addkid(Node("e"))
                )

        e = EditPathGenerator(A,B)
        self.assertEqual(1, e.get_tree_dist())
        self.assert_insert(e.get_tree_edits(), "X")

    def test_remove(self):
        A = (
            Node("f")
                .addkid(Node("d")
                    .addkid(Node("a"))
                    .addkid(Node("X"))
                    .addkid(Node("c")
                        .addkid(Node("b"))))
                .addkid(Node("e"))
                )
        B = (
            Node("f")
                .addkid(Node("d")
                    .addkid(Node("a"))
                    .addkid(Node("c")
                        .addkid(Node("b"))))
                .addkid(Node("e"))
                )

        e = EditPathGenerator(A,B)
        self.assertEqual(1, e.get_tree_dist())
        self.assert_remove(e.get_tree_edits(), "X")

    def test_update(self):
        A = (
            Node("f")
                .addkid(Node("d")
                    .addkid(Node("a"))
                    .addkid(Node("c")
                        .addkid(Node("b"))))
                .addkid(Node("e"))
                )
        B = (
            Node("f")
                .addkid(Node("d")
                    .addkid(Node("a"))
                    .addkid(Node("c")
                        .addkid(Node("B"))))
                .addkid(Node("e"))
                )

        e = EditPathGenerator(A,B)
        self.assertEqual(1, e.get_tree_dist())
        self.assert_update(e.get_tree_edits(), "b", "B")

    def test_multiple_insert(self):
        A = (
            Node("f")
                .addkid(Node("d")
                    .addkid(Node("a"))
                    .addkid(Node("c")
                        .addkid(Node("b"))))
                .addkid(Node("e"))
                )
        B = (
            Node("f")
                .addkid(Node("d")
                    .addkid(Node("a"))
                    .addkid(Node("X"))
                    .addkid(Node("c")
                        .addkid(Node("b"))))
                .addkid(Node("e")
                    .addkid(Node("Y")))
                )

        e = EditPathGenerator(A,B)
        self.assertEqual(2, e.get_tree_dist())
        self.assert_insert(e.get_tree_edits(), "X")
        self.assert_insert(e.get_tree_edits(), "Y")

    def test_multiple_remove(self):
        B = (
            Node("f")
                .addkid(Node("d")
                    .addkid(Node("a"))
                    .addkid(Node("c")
                        .addkid(Node("b"))))
                .addkid(Node("e"))
                )
        A = (
            Node("f")
                .addkid(Node("d")
                    .addkid(Node("a"))
                    .addkid(Node("X"))
                    .addkid(Node("c")
                        .addkid(Node("b"))))
                .addkid(Node("e")
                    .addkid(Node("Y")))
                )

        e = EditPathGenerator(A,B)
        self.assertEqual(2, e.get_tree_dist())
        self.assert_remove(e.get_tree_edits(), "X")
        self.assert_remove(e.get_tree_edits(), "Y")

    def test_multiple_update(self):
        A = (
            Node("f")
                .addkid(Node("d")
                    .addkid(Node("a"))
                    .addkid(Node("c")
                        .addkid(Node("b"))))
                .addkid(Node("e"))
                )

        B = (
            Node("X")
                .addkid(Node("d")
                    .addkid(Node("a"))
                    .addkid(Node("Y")
                        .addkid(Node("b"))))
                .addkid(Node("e"))
                )
        e = EditPathGenerator(A,B)
        self.assertEqual(2, e.get_tree_dist())
        self.assert_update(e.get_tree_edits(), "f", "X")
        self.assert_update(e.get_tree_edits(), "c", "Y")

    def test_insert_subtree(self):
        A = (
            Node("f")
                .addkid(Node("e"))
                )
        B = (
            Node("f")
                .addkid(Node("d")
                    .addkid(Node("a"))
                    .addkid(Node("c")
                        .addkid(Node("b"))))
                .addkid(Node("e"))
                )

        e = EditPathGenerator(A,B)
        self.assertEqual(4, e.get_tree_dist())
        self.assert_insert(e.get_tree_edits(), "d")
        self.assert_insert(e.get_tree_edits(), "a")
        self.assert_insert(e.get_tree_edits(), "c")
        self.assert_insert(e.get_tree_edits(), "b")

 
    def test_remove_subtree(self):
        B = (
            Node("f")
                .addkid(Node("e"))
                )
        A = (
            Node("f")
                .addkid(Node("d")
                    .addkid(Node("a"))
                    .addkid(Node("c")
                        .addkid(Node("b"))))
                .addkid(Node("e"))
                )

        e = EditPathGenerator(A,B)
        self.assertEqual(4, e.get_tree_dist())
        self.assert_remove(e.get_tree_edits(), "d")
        self.assert_remove(e.get_tree_edits(), "a")
        self.assert_remove(e.get_tree_edits(), "c")
        self.assert_remove(e.get_tree_edits(), "b")

from zss.edit import get_edit_path_generator_from_set_tree as get_from_set_tree
from zss.simple_tree import SetNode
 
class FromSetTreeTestCase(TestCase):

    def test_base(self):
        o = (
                Node("a")
                    .addkid(Node("b"))
                    .addkid(Node("c"))
                    )

        s = (
                SetNode("a")
                    .addkid(Node("b"))
                    .addkid(Node("c"))
                    )

        epg = get_from_set_tree(o, s)
        self.assertEqual(epg.get_tree_dist(), 0)


    def test_simple(self):
        o = (
                Node("a")
                    .addkid(Node("b"))
                    .addkid(Node("c"))
                    )

        s = (
                SetNode("a")
                    .addkid(Node("b"))
                    .addkid(Node("e"))
                    )

        epg = get_from_set_tree(o, s)
        self.assertEqual(epg.get_tree_dist(), 1)
