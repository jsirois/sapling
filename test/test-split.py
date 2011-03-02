import fixtures
import saplib
import unittest

class SplitTest(unittest.TestCase, fixtures.RepoFixture):
  def test_name_only(self):
    split = saplib.Split(self.repo(), 'jake', [])
    self.assertEquals('jake', split.name)
    self.assertEquals([], split.paths)

  def test_invalid(self):
    self.assertRaises(KeyError, saplib.Split, self.repo(), 'jake', [ 'baz/' ])
    self.assertRaises(KeyError, saplib.Split, self.repo(), 'jake', [ 'test', 'baz' ])

  def test_simple(self):
    split = saplib.Split(self.repo(), 'jake', [ 'test', 'saplib' ])
    self.assertEquals('jake', split.name)
    self.assertEquals([ 'test', 'saplib' ], split.paths)
