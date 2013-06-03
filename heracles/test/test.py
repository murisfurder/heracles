from os.path import dirname, realpath, join
import ctypes as c
from unittest import TestCase
from heracles import Heracles, Tree, ListTree, TreeNode, ListTreeNode
from heracles.raw import ManagedRawTree 
from heracles.tree import check_list_nodes

CURRENT_DIR = dirname(realpath(__file__))
DATA_FILE = join(CURRENT_DIR, "data/sources.list")

heracles = Heracles()
def check_equal_addresses(p1, p2):
    return c.addressof(p1) == c.addressof(p2)

def check_equal_tree(test, tree1, tree2):
    for t1, t2 in zip(tree1, tree2):
        test.assertEqual(t1.label, t2.label)
        test.assertEqual(t1.value, t2.value)
        check_equal_tree(test, t1.children, t2.children)

def check_serialized_equal(test, data, tree):
    for s, o in zip(data, tree):
        test.assertEqual(s['label'], o.label)
        test.assertEqual(s['value'], o.value)
        check_serialized_equal(test, s['children'], o.children)

class HeraclesTest(TestCase):
    def setUp(self):
        self.text = file(DATA_FILE).read()
        self.lens = heracles.lenses['Aptsources']
        self.tree = self.lens.get(self.text)

    def test_list(self):
        self.assertTrue(isinstance(self.tree, ListTree))

    def test_get_and_put(self):
        gtext = self.lens.put(self.tree, self.text)
        ntree = self.lens.get(gtext)
        check_equal_tree(self, self.tree, ntree)

    def test_delete_row(self):
        self.tree.remove(self.tree["1"][0])
        text = self.lens.put(self.tree, "")
        ntree = self.lens.get(text)
        check_equal_tree(self, self.tree, ntree)

    def test_list_tree(self):
        self.assertEqual(self.tree[0].value, "")

class FilterTest(TestCase):
    def setUp(self):
        self.text = file(DATA_FILE).read()
        self.lens = heracles.lenses['Aptsources']

    def test_filter(self):
        self.assertTrue(self.lens.check_path("/etc/apt/sources.list"))
        self.assertFalse(self.lens.check_path("/etc/sources.list"))

    def test_get_lens(self):
        l = heracles.get_lens_by_path("/etc/apt/sources.list")
        self.assertEqual(l.name, "Aptsources")
        l = heracles.get_lens_by_path("/etc/sudoers")
        self.assertEqual(l.name, "Sudoers")
        l = heracles.get_lens_by_path("/etc/xudoers")
        self.assertTrue(l is None)

class TreeBuildTest(TestCase):
    def test_build_list_tree(self):
        t = Tree()
        t['1'] = "a"
        t['2'] = "b"
        t['3'] = "c"
        self.assertTrue(check_list_nodes(t._nodes))
        rt = ManagedRawTree.build_from_tree(t)
        nt = rt.build_tree()
        self.assertTrue(isinstance(nt, ListTree))

    def test_build_list_tree_2(self):
        t = Tree()
        t['3'] = "a"
        t['2'] = "b"
        t['1'] = "c"
        self.assertFalse(check_list_nodes(t._nodes))
        rt = ManagedRawTree.build_from_tree(t)
        nt = rt.build_tree()
        self.assertFalse(isinstance(nt, ListTree))

    def test_build_list_tree_3(self):
        t = Tree()
        t['1'] = "c"
        t['1'] = "x"
        t['2'] = "b"
        t['3'] = "a"
        self.assertFalse(check_list_nodes(t._nodes))
        rt = ManagedRawTree.build_from_tree(t)
        nt = rt.build_tree()
        self.assertFalse(isinstance(nt, ListTree))

class TreeTest(TestCase):
    def setUp(self):
        self.t = Tree()
        self.t['a'] = 'a1'
        self.t['b'] = 'b1'
        self.t['c'] = 'c1'
        self.t['d'] = 'd1'
        self.t['d'] = 'd2'
        t2 = self.t['a'][0].children
        t2['a11'] = 'a11'
        t2['a12'] = 'a12'
        t2['a13'] = 'a13'
        t2['a14'] = 'a141'
        t2['a14'] = 'a142'

    def tearDown(self):
        del self.t

    def test_repr(self):
        self.assertTrue(len(str(self.t)) > 0)

    def test_tree(self):
        self.assertEqual(self.t['a'].value, 'a1')
        self.assertEqual(self.t['b'].value, 'b1')
        self.assertEqual(self.t['c'].value, 'c1')
        self.assertEqual(self.t['d'][0].value, 'd1')
        self.assertEqual(self.t['d'][1].value, 'd2')
        self.assertEqual(self.t['d']['d1'].value, 'd1')
        self.assertEqual(self.t['d']['d2'].value, 'd2')
        self.assertTrue('a' in self.t)
        self.assertTrue('b' in self.t)
        self.assertTrue('c' in self.t)
        self.assertTrue('d' in self.t)
        t2 = self.t['a'].children
        self.assertEqual(t2['a11'].value, 'a11')
        self.assertEqual(t2['a11'].parent, self.t['a'][0])
        self.assertEqual(t2['a12'].value, 'a12')
        self.assertEqual(t2['a12'].parent, self.t['a'][0])
        self.assertEqual(t2['a13'].value, 'a13')
        self.assertEqual(t2['a13'].parent, self.t['a'][0])
        self.assertEqual(t2['a14'][0].value, 'a141')
        self.assertEqual(t2['a14'][0].parent, self.t['a'][0])
        self.assertEqual(t2['a14'][1].value, 'a142')
        self.assertEqual(t2['a14'][1].parent, self.t['a'][0])
        self.assertTrue('a11' in t2)
        self.assertTrue('a12' in t2)
        self.assertTrue('a13' in t2)
        self.assertTrue('a14' in t2)

    def test_insert_1(self):
        node = TreeNode(label="x", value="x1")
        self.t.insert(0, node)
        self.assertTrue('x' in self.t)
        self.assertEqual(self.t.index(node), 0)

    def test_insert_2(self):
        node = TreeNode(label="x", value="x1")
        self.t['a'].children.insert(0, node)
        self.assertTrue('x' in self.t['a'].children)
        self.assertEqual(self.t['a'].children.index(node), 0)

    def test_append_1(self):
        node = TreeNode(label="x", value="x1")
        self.t.append(node)
        self.assertTrue('x' in self.t)
        self.assertEqual(self.t.index(node), len(self.t)-1)

    def test_append_2(self):
        node = TreeNode(label="x", value="x1")
        self.t['a'].children.append(node)
        self.assertTrue('x' in self.t['a'].children)
        self.assertEqual(self.t['a'].children.index(node), len(self.t['a'].children) - 1)

    def test_remove_1(self):
        node = self.t['a'][0]
        self.t.remove(node)
        self.assertFalse('a' in self.t)

    def test_remove_2(self):
        node = self.t['a'].children['a11'][0]
        self.t['a'].children.remove(node)
        self.assertFalse('a11' in self.t['a'].children)

    def test_add_new_node(self):
        self.t.add_new_node(label="x", value="x1")
        self.assertEqual(len(self.t), 6)
        self.assertEqual(self.t[-1].label, "x")
        self.assertEqual(self.t[-1].value, "x1")
        self.assertTrue(isinstance(self.t[-1], TreeNode))

    def test_add_new_list_node(self):
        self.t.add_new_list_node(label="x", value="x1")
        self.assertEqual(len(self.t), 6)
        self.assertEqual(self.t[-1].label, "x")
        self.assertEqual(self.t[-1].value, "x1")
        self.assertTrue(isinstance(self.t[-1], ListTreeNode))

    def test_insert_new_node(self):
        self.t.insert_new_node(2, label="x", value="x1")
        self.assertEqual(len(self.t), 6)
        self.assertEqual(self.t[2].label, "x")
        self.assertEqual(self.t[2].value, "x1")
        self.assertTrue(isinstance(self.t[2], TreeNode))

    def test_insert_new_list_node(self):
        self.t.insert_new_list_node(2, label="x", value="x1")
        self.assertEqual(len(self.t), 6)
        self.assertEqual(self.t[2].label, "x")
        self.assertEqual(self.t[2].value, "x1")
        self.assertTrue(isinstance(self.t[2], TreeNode))

class LabelNodeListTest(TestCase):
    def setUp(self):
        self.t = Tree()
        self.t['a'] = "1"
        self.t['a'] = "2"
        self.t['b'] = "x"
        self.t['a'] = "3"
        self.t['a'] = "4"
        self.l = self.t['a']
    
    def test_repr(self):
        self.assertTrue(len(self.l.__repr__()) > 0)

    def test_labelnodelist(self):
        self.assertEqual(len(self.l), 4)

    def test_single_node(self):
        self.assertEqual(self.t['b'].value, "x")
        self.t['b'].value = "x1"
        self.assertEqual(self.t['b'].value, "x1")
        self.assertTrue(isinstance(self.t['b'].children, Tree))
        self.assertTrue(self.t['b'].parent is None)

    def test_insert_1(self):
        self.l.insert(2,"xx")
        self.assertEqual(self.l[2].value, "xx")
        self.assertEqual(self.t[3].value, "xx")

    def test_insert_2(self):
        self.l.insert(-1,"xx")
        self.assertEqual(self.l[-1].value, "xx")
        self.assertEqual(self.l[4].value, "xx")

    def test_append(self):
        self.l.append("xx")
        self.assertEqual(self.l[-1].value, "xx")

    def test_remove(self):
        n = self.l[1]
        self.l.remove(n)
        self.assertFalse(n in self.t)
        self.assertEqual(len(self.l), 3)

    def test_contains(self):
        self.assertTrue("1" in self.t['a'])
        self.assertTrue("2" in self.t['a'])
        self.assertTrue("3" in self.t['a'])
        self.assertTrue("4" in self.t['a'])

class ListTreeTest(TestCase):
    def setUp(self):
        self.t = ListTree()
        self.t.add_new_list_node('a1')
        self.t['#comment'] = 'comment'
        self.t.add_new_node('b1')
        self.t.add_new_node('c1')
        self.t.add_new_node('d1')
        t2 = self.t[0].children
        t2.add_new_node('a11')
        t2.add_new_node('a12')
        t2['#comment'] = 'comment'
        t2.add_new_node('a13')
        t2.add_new_node('a14')

    def check_list_tree_sanity(self, t):
        i = 1
        for n in t._nodes:
            try:
                n_i = int(n.label)
                if n_i != i:
                    self.fail('Insane tree')
                i += 1
            except:
                pass

    def tearDown(self):
        del self.t

    def test_repr(self):
        self.assertTrue(len(str(self.t)) > 0)

    def test_tree(self):
        self.check_list_tree_sanity(self.t)
        self.assertTrue(isinstance(self.t, ListTree))
        self.assertEqual(self.t[0].value, 'a1')
        self.assertEqual(self.t[1].value, 'b1')
        self.assertEqual(self.t[2].value, 'c1')
        self.assertEqual(self.t[3].value, 'd1')
        self.assertTrue('a1' in self.t)
        self.assertTrue('b1' in self.t)
        self.assertTrue('c1' in self.t)
        self.assertTrue('d1' in self.t)
        t = self.t[0]
        t2 = t.children
        self.assertTrue(isinstance(t2, ListTree))
        self.assertEqual(t2[0].value, 'a11')
        self.assertEqual(t2[0].parent, t)
        self.assertEqual(t2[1].value, 'a12')
        self.assertEqual(t2[1].parent, t)
        self.assertEqual(t2[2].value, 'a13')
        self.assertEqual(t2[2].parent, t)
        self.assertEqual(t2[3].value, 'a14')
        self.assertEqual(t2[3].parent, t)
        self.assertTrue('a11' in t2)
        self.assertTrue('a12' in t2)
        self.assertTrue('a13' in t2)
        self.assertTrue('a14' in t2)

    def test_insert_1(self):
        n = TreeNode(value="x")
        self.t.insert(2,n)
        self.assertEqual(self.t[2].value, "x")
        self.assertEqual(self.t[2].label, "3")
        self.check_list_tree_sanity(self.t)

    def test_insert_2(self):
        n = TreeNode(value="x")
        t = self.t[0].children
        t.insert(2,n)
        self.assertEqual(t[2].value, "x")
        self.assertEqual(t[2].label, "3")
        self.check_list_tree_sanity(self.t[0].children)

    def test_append_1(self):
        n = TreeNode(value="x")
        self.t.append(n)
        self.assertEqual(self.t[4].value, "x")
        self.assertEqual(self.t[4].label, "5")
        self.assertEqual(self.t[-1].value, "x")
        self.assertEqual(self.t[-1].label, "5")
        self.check_list_tree_sanity(self.t)

    def test_append_2(self):
        n = TreeNode(value="x")
        t = self.t[0].children
        t.append(n)
        self.assertEqual(t[4].value, "x")
        self.assertEqual(t[4].label, "5")
        self.assertEqual(t[-1].value, "x")
        self.assertEqual(t[-1].label, "5")
        self.check_list_tree_sanity(self.t[0].children)

    def test_remove_1(self):
        n = self.t[2]
        self.t.remove(n)
        self.assertEqual(self.t[2].value, "d1")
        self.assertEqual(self.t[2].label, "3")
        self.assertTrue(len(self.t), 3)
        self.check_list_tree_sanity(self.t)

    def test_remove_2(self):
        t = self.t[0].children
        n = t[2]
        t.remove(n)
        self.assertEqual(t[2].value, "a14")
        self.assertEqual(t[2].label, "3")
        self.assertTrue(len(t), 3)
        self.check_list_tree_sanity(t)

    def test_index(self):
        t = self.t[0].children
        for i in range(0,4):
            self.assertEqual(self.t.index(self.t[i]), i)
            self.assertEqual(t.index(t[i]), i)

    def test_add_new_node(self):
        self.t.add_new_node("x")
        self.assertEqual(len(self.t), 5)
        self.assertEqual(self.t[-1].value, "x")
        self.assertTrue(isinstance(self.t[-1], TreeNode))

    def test_add_new_list_node(self):
        self.t.add_new_list_node("x")
        self.assertEqual(len(self.t), 5)
        self.assertEqual(self.t[-1].value, "x")
        self.assertTrue(isinstance(self.t[-1], ListTreeNode))

    def test_insert_new_node(self):
        self.t.insert_new_node(2, "x")
        self.assertEqual(len(self.t), 5)
        self.assertEqual(self.t[2].value, "x")
        self.assertTrue(isinstance(self.t[2], TreeNode))

    def test_insert_new_list_node(self):
        self.t.insert_new_list_node(2, "x")
        self.assertEqual(len(self.t), 5)
        self.assertEqual(self.t[2].value, "x")
        self.assertTrue(isinstance(self.t[2], ListTreeNode))

class ListTreeTextAsTable(TestCase):
    def setUp(self):
        t = ListTree()
        n = t.add_new_node("")
        n.children.add_new_node(label="name", value="Pepe")
        n.children.add_new_node(label="surname", value="Diaz")
        n.children.add_new_node(label="tel", value="555-0000")
        n = t.add_new_node("")
        n.children.add_new_node(label="name", value="Juan")
        n.children.add_new_node(label="surname", value="Gonzalez")
        n.children.add_new_node(label="tel", value="555-0001")
        n = t.add_new_node("")
        n.children.add_new_node(label="name", value="Ramon")
        n.children.add_new_node(label="surname", value="Diaz")
        n.children.add_new_node(label="tel", value="555-0002")
        n = t.add_new_node("")
        n.children.add_new_node(label="name", value="Maria")
        n.children.add_new_node(label="surname", value="Rodriguez")
        n.children.add_new_node(label="tel", value="555-0003")
        self.t = t

    def test_search_1(self):
        l = self.t.search(name="Pepe", surname="Diaz")
        self.assertEqual(len(l), 1)
        n = l[0]
        self.assertTrue("555-0000" in n.children['tel'])

    def test_search_2(self):
        l = self.t.search(surname="Diaz")
        self.assertEqual(len(l), 2)
        n = l[0]
        self.assertTrue("555-0000" in n.children['tel'])
        n = l[1]
        self.assertTrue("555-0002" in n.children['tel'])


if __name__ == "__main__":
    import unittest
    unittest.main()

