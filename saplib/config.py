from lib import with_line_numbers
from split import Split
import traceback

class ConfigError(Exception):
  """Thrown when a Config cannot parse."""

  def __init__(self, msg, *args):
    self.msg = msg % args

  def __str__(self):
    return self.msg


class Config(object):
  """Represents a sapling split configuration.  Configurations can contain any valid python code
  but need only define a splits list containing the splits in a git repository.  Each split is a
  dict that must have the following entries:
  'name': a logical name for the split
  'paths': the paths this split is comprised of relative to the root of the git repository
  """

  __slots__ = ('_splits')

  def __init__(self, repo, data = None):
    if data is None or len(data) == 0 or data.isspace():
      self._splits = {}
    else:
      self._splits = Config._parse(repo, data.strip())

  @classmethod
  def _parse(cls, repo, config):
    local_config = {}
    try:
      exec(config, {}, local_config)
    except StandardError:
      raise ConfigError("Problem parsing config:\n%s\n\n%s", with_line_numbers(config),
                        traceback.format_exc())

    Config._validate(local_config)

    splits = {}
    for splitmap in local_config['splits']:
      split = Config._parse_split(repo, splitmap)
      splits[split.name] = split
    return splits

  @classmethod
  def _parse_split(cls, repo, splitmap):
    name = splitmap.pop('name')
    patterns = splitmap.pop('paths')
    try:
      return Split(repo, name, patterns)
    except KeyError:
      raise ConfigError("Problem creating split: %s\n%s\n\n%s", name, splitmap,
                        traceback.format_exc())

  @classmethod
  def _validate(cls, config):
    if 'splits' in config:
      for split in config['splits']:
        Config._validate_split(split)

  @classmethod
  def _validate_split(cls, split):
    problems = []
    if 'name' not in split:
      problems.append("split must define a 'name'")
    if 'paths' not in split:
      problems.append("split must define 'paths'")
    if len(problems) > 0:
      raise ConfigError("Invalid split %s has the following problems:\n\t%s", split,
                        '\n\t'.join(problems))

  @property
  def splits(self):
    """A dict of the configured Splits keyed by their names."""
    return self._splits

  def __str__(self):
    return "Config(%s)" % ", ".join('%s => %s' % (x, y) for (x, y) in self.splits.items())
