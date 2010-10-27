class Split(object):
  """Represents a split of a git repository off to a remote repository.  A Split maps one or more
  subtrees of a containing git repository as a logical unit that can be pushed to or pulled from its
  remote."""

  __slots__ = ('_name', 'remote', 'paths')

  def __init__(self, name, map = None):
    self._name = name
    if map is not None:
      self.remote = map.get('remote', None)
      self.paths = map.get('paths', [])
    else:
      self.remote = None
      self.paths = []

  @property
  def name(self):
    """The logical name of this Split."""
    return self._name

  def __str__(self):
    return "Split(name=%s, remote=%s, paths=%s)" % (self._name, self.remote, self.paths)



