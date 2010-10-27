import gitsap
import traceback

class ConfigError(Exception):
  """Thrown when a Config cannot parse."""

  def __init__(self, msg, *args):
    self.msg = msg % args

  def __str__(self):
    return self.msg


class Config(object):
  """Represents a git-sap split configuration."""

  __slots__ = ['_splits']

  def __init__(self, data = None):
    if data is None or len(data) == 0 or data.isspace():
      self._splits = {}
    else:
      self._splits = Config._parse(data.strip())

  @classmethod
  def _parse(cls, config):
    local_config = {}
    try:
      exec(config, {}, local_config)
    except SyntaxError:
      raise ConfigError("Problem parsing config: %s\n\n%s", config, traceback.format_exc())

    Config._validate(local_config)

    splits = {}
    for splitmap in local_config['splits']:
      split = Config._parse_split(splitmap)
      splits[split.name] = split
    return splits

  @classmethod
  def _parse_split(cls, splitmap):
    name = splitmap.pop('name')
    return gitsap.Split(name, splitmap)

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
    if 'remote' not in split:
      problems.append("split must define a 'remote'")
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
    return "Config(%s)" % ", ".join(map(lambda (x, y): '%s => %s' % (x, y), self.splits.items()))
