from unittest import TestCase
from heracles.compare import MultipleKeysDict, SortedKeysDict, \
        HeraclesSortedKeysDictError

class TestMKD(MultipleKeysDict):
    sorted_multiple_keys = ("sorted")
    unsorted_multiple_keys = ("unsorted")

class MulipleKeysDictTestCase(TestCase):
    def test_setitem(self):
        d = TestMKD()
        d._setitem("prueba", 1)
        self.assertEqual(d["prueba"], 1)

    def test_load_data_base(self):
        simple = dict(a=1, b=2, c=3)
        d = TestMKD()
        d._load_data(simple)
        self.assertEqual(d["a"], 1)
        self.assertEqual(d["b"], 2)
        self.assertEqual(d["c"], 3)

    def test_load_data_sorted_1(self):
        simple = dict(a=1, b=2, sorted=(1,2,3))
        d = TestMKD()
        d._load_data(simple)
        self.assertEqual(d["a"], 1)
        self.assertEqual(d["b"], 2)
        self.assertEqual(d["sorted"], [1,2,3])

    def test_load_data_sorted_2(self):
        simple = dict(a=1, b=2, sorted=(3))
        d = TestMKD()
        d._load_data(simple)
        self.assertEqual(d["a"], 1)
        self.assertEqual(d["b"], 2)
        self.assertEqual(d["sorted"], [3])

    def test_load_data_unsorted_1(self):
        simple = dict(a=1, b=2, unsorted=(1,2,3))
        d = TestMKD()
        d._load_data(simple)
        self.assertEqual(d["a"], 1)
        self.assertEqual(d["b"], 2)
        self.assertEqual(d["unsorted"], set((1,2,3)))

    def test_load_data_usorted_2(self):
        simple = dict(a=1, b=2, unsorted=(3))
        d = TestMKD()
        d._load_data(simple)
        self.assertEqual(d["a"], 1)
        self.assertEqual(d["b"], 2)
        self.assertEqual(d["unsorted"], set((3,)))

    def test_setitem_base(self):
        d = TestMKD()
        d["a"] = 1
        self.assertEqual(d["a"], 1)

    def test_setitem_sorted(self):
        d = TestMKD()
        d["sorted"] = 1
        self.assertEqual(d["sorted"], [1])
        d["sorted"] = 2
        self.assertEqual(d["sorted"], [1,2])

    def test_setitem_unsorted(self):
        d = TestMKD()
        d["unsorted"] = 1
        self.assertEqual(d["unsorted"], set([1]))
        d["unsorted"] = 2
        self.assertEqual(d["unsorted"], set([1,2]))

class TestSKD(SortedKeysDict):
    key_order = ("c", "b", "a")

class SortedKeysDictTestCase(TestCase):
    
    def setUp(self):
        self.d = TestSKD(a=1, b=2, c=3, d=4, e=5)

    def test_key_requirement(self):
        d = TestSKD()
        d["c"] = 1
        self.assertRaises(HeraclesSortedKeysDictError, d.check)

    def test_notorderedkeys(self):
        self.assertEqual(set(self.d.iternotorderedkeys()), set(("d", "e")))
        self.assertEqual(set(self.d.notorderedkeys()), set(("d", "e")))

    def test_iterkeys(self):
        l = list(self.d.iterkeys())
        self.assertEqual(l[0], "c")
        self.assertEqual(l[1], "b")
        self.assertEqual(l[2], "a")
        self.assertEqual(set(l[3:]), set(("d","e")))
        l = list(self.d.keys())
        self.assertEqual(l[0], "c")
        self.assertEqual(l[1], "b")
        self.assertEqual(l[2], "a")
        self.assertEqual(set(l[3:]), set(("d","e")))

    def test_values(self):
        l = list(self.d.itervalues())
        self.assertEqual(l[0], 3)
        self.assertEqual(l[1], 2)
        self.assertEqual(l[2], 1)
        self.assertEqual(set(l[3:]), set((4,5)))
        l = list(self.d.values())
        self.assertEqual(l[0], 3)
        self.assertEqual(l[1], 2)
        self.assertEqual(l[2], 1)
        self.assertEqual(set(l[3:]), set((4,5)))

    def test_items(self):
        l = list(self.d.iteritems())
        self.assertEqual(l[0], ("c",3))
        self.assertEqual(l[1], ("b",2))
        self.assertEqual(l[2], ("a",1))
        self.assertEqual(set(l[3:]), set((("d",4),("e",5))))
        l = list(self.d.items())
        self.assertEqual(l[0], ("c",3))
        self.assertEqual(l[1], ("b",2))
        self.assertEqual(l[2], ("a",1))
        self.assertEqual(set(l[3:]), set((("d",4),("e",5))))


















