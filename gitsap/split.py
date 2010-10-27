class Split(object):
  """Represents a split of a git repository off to a remote repository.  A Split maps one or more
  subtrees of a containing git repository as a logical unit that can be pushed to or pulled from its
  remote."""

  __slots__ = ('_repo', '_name', 'remote', '_paths')

  def __init__(self, repo, name, map = None):
    self._repo = repo
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

  @property
  def paths(self):
    return self._paths

  @paths.setter
  def paths(self, value):
    self._paths = self._validate_paths(value)

  def _validate_paths(self, paths):
    tree = self._current_tree()
    for path in paths:
      try:
        tree / path
      except KeyError:
        raise KeyError("Invalid path: %s" % path)
    return paths

  def subtrees(self):
    tree = self._current_tree()
    for path in self.paths:
      yield tree / path

  def _current_tree(self):
    return self._repo.head.commit.tree

  def __str__(self):
    return "Split(name=%s, remote=%s, paths=%s)" % (self._name, self.remote, self.paths)
