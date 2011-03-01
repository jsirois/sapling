import fixtures
import saplib
import unittest

class TestConfig(unittest.TestCase, fixtures.RepoFixture):
  def test_empty_config(self):
    self.assertEquals(0, len(self._create_config("splits = []").splits))
    self.assertEquals(0, len(self._create_config("").splits))
    self.assertEquals(0, len(self._create_config().splits))

  def test_invalid_split(self):
    self._assert_config_error("splits = [{}]")
    self._assert_config_error("splits = [{'paths': []}]")

  def test_simple_split(self):
    config = self._create_config("""
test = {
  'name': 'test',
  'paths': [
    'test',
  ]
}
splits = [ test ]""")

    self.assertTrue('test' in config.splits)
    split = config.splits['test']
    self.assertEquals('test', split.name)
    self.assertEquals(['test'], split.paths)

  def _assert_config_error(self, config):
    self.assertRaises(saplib.ConfigError, saplib.Config, self.repo(), config)

  def _create_config(self, config = None):
    return saplib.Config(self.repo(), config)
