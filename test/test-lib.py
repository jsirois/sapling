import saplib
import unittest

class LibTest(unittest.TestCase):
  def test_find(self):
    self.assertEqual(2, saplib.find([1, 2, 3], lambda x: x > 1))
    self.assertEqual(2, saplib.find([1, 2, 3], lambda x: x == 4, 2))

    self.assertEqual(2, saplib.find([1, 2, 3], lambda x: x == 2,
                                    lambda: self.fail("unexpected application of callable")))
    self.assertEqual("delayed", saplib.find([1, 2, 3], lambda x: x == 4, lambda: "delayed"))
    self.assertRaises(KeyError, saplib.find, [1, 2, 3], lambda x: x == 4)

  def test_with_line_numbers(self):
    self.assertEqual("1 ", saplib.with_line_numbers(""))
    self.assertEqual("1 a", saplib.with_line_numbers("a"))
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
11 k""", saplib.with_line_numbers("""a
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
