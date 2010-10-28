import gitsap
import unittest

class LibTest(unittest.TestCase):
  def test_find(self):
    self.assertEqual(2, gitsap.find([1, 2, 3], lambda x: x > 1))
    self.assertEqual(2, gitsap.find([1, 2, 3], lambda x: x == 4, 2))

    self.assertEqual(2, gitsap.find([1, 2, 3], lambda x: x == 2,
                                    lambda: self.fail("unexpected application of callable")))
    self.assertEqual("delayed", gitsap.find([1, 2, 3], lambda x: x == 4, lambda: "delayed"))
    self.assertRaises(KeyError, gitsap.find, [1, 2, 3], lambda x: x == 4)

  def test_with_line_numbers(self):
    self.assertEqual("1 ", gitsap.with_line_numbers(""))
    self.assertEqual("1 a", gitsap.with_line_numbers("a"))
    self.assertEqual(""" 1 a
 2 b
 3  c
 4   d
 5    e
 6     f
 7      g
 8       h
 9        i
10         j
11 k""", gitsap.with_line_numbers("""a
b
 c
  d
   e
    f
     g
      h
       i
        j
k""".strip()))
