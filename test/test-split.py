import fixtures
import gitsap
import unittest

class SplitTest(unittest.TestCase, fixtures.RepoFixture):
  def test_name_only(self):
    split = gitsap.Split(self.repo(), 'jake')
    self.assertEquals('jake', split.name)
    self.assertEquals(None, split.remote)
    self.assertEquals([], split.paths)
