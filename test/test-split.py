import unittest
import gitsap

class SplitTest(unittest.TestCase):
  def test_name_only(self):
    split = gitsap.Split('jake')
    self.assertEquals('jake', split.name)
    self.assertEquals(None, split.remote)
    self.assertEquals([], split.paths)
