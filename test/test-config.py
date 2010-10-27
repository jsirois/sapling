import fixtures
import gitsap
import unittest

class TestConfig(unittest.TestCase, fixtures.RepoFixture):
  def test_empty_config(self):
    self.assertEquals(0, len(self._create_config("splits = []").splits))
    self.assertEquals(0, len(self._create_config("").splits))
    self.assertEquals(0, len(self._create_config().splits))

  def test_invalid_split(self):
    self._assert_config_error("splits = [{}]")
    self._assert_config_error("splits = [{'remote': 'common'}]")
    self._assert_config_error("splits = [{'paths': []}]")

  def test_simple_split(self):
    config = self._create_config("""
test = {
  'name': 'test',
  'remote': 'file:/tmp/git-sap-tests.git',
  'paths': [
    'test',
  ]
}
splits = [ test ]""")

    self.assertTrue('test' in config.splits)
    split = config.splits['test']
    self.assertEquals('test', split.name)
    self.assertEquals('file:/tmp/git-sap-tests.git', split.remote)
    self.assertEquals(['test'], split.paths)

  def _assert_config_error(self, config):
    self.assertRaises(gitsap.ConfigError, gitsap.Config, self.repo(), config)

  def _create_config(self, config = None):
    return gitsap.Config(self.repo(), config)
