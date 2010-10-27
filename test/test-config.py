import unittest
import gitsap

class TestConfig(unittest.TestCase):
  def test_empty_config(self):
    self.assertEquals(0, len(gitsap.Config("splits = []").splits))
    self.assertEquals(0, len(gitsap.Config("").splits))
    self.assertEquals(0, len(gitsap.Config().splits))

  def test_invalid_split(self):
    self.assertRaises(gitsap.ConfigError, gitsap.Config, "splits = [{}]")
    self.assertRaises(gitsap.ConfigError, gitsap.Config, "splits = [{'remote': 'common'}]")
    self.assertRaises(gitsap.ConfigError, gitsap.Config, "splits = [{'paths': []}]")

  def test_simple_split(self):
    config = gitsap.Config("""
common = {
  'name': 'common',
  'remote': 'http://github.com/git-sap.git',
  'paths': [
    'modules/common',
    'src/main/python/common',
    'src/test/python/common'
  ]
}
splits = [ common ]""")

    self.assertTrue('common' in config.splits)
    split = config.splits['common']
    self.assertEquals('common', split.name)
    self.assertEquals('http://github.com/git-sap.git', split.remote)
    self.assertEquals(['modules/common', 'src/main/python/common', 'src/test/python/common'],
                      split.paths)
