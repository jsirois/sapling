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
