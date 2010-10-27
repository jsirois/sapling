import fixtures
import gitsap
import unittest

class SplitTest(unittest.TestCase, fixtures.RepoFixture):
  def test_name_only(self):
    split = gitsap.Split(self.repo(), 'jake')
    self.assertEquals('jake', split.name)
    self.assertEquals(None, split.remote)
    self.assertEquals([], split.paths)

  def test_invalid(self):
    self.assertRaises(KeyError, gitsap.Split, self.repo(), 'jake', paths = [ 'test/' ])
    self.assertRaises(KeyError, gitsap.Split, self.repo(), 'jake', paths = [ 'test', 'baz' ])

  def test_simple(self):
    split = gitsap.Split(self.repo(), 'jake',
                         remote = 'file:/tmp/fake.git',
                         paths = [ 'test', 'gitsap' ])
    self.assertEquals('jake', split.name)
    self.assertEquals('file:/tmp/fake.git', split.remote)
    self.assertEquals([ 'test', 'gitsap' ], split.paths)
