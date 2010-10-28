import git

class Split(object):
  """Represents a split of a git repository off to a remote repository.  A Split maps one or more
  subtrees of a containing git repository as a logical unit that can be pushed to or pulled from its
  remote."""

  __slots__ = ('_repo', '_name', 'remote', '_paths')

  def __init__(self, repo, name, **kwargs):
    """Creates a new Split over the given repo with the specified logical name.  The 'remote' git
    url and the 'paths' to split out can be specified as keyword arguments"""
    self._repo = repo
    self._name = name
    self.remote = kwargs.get('remote', None)
    self.paths = kwargs.get('paths', [])

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

  def subtrees(self, commit = None):
    if commit is None:
      commit = self._current_head()

    for path in self.paths:
      yield commit.tree / path

  def commits(self, reverse = True):
    head = self._current_head()
    return git.Commit.iter_items(self._repo, head, self.paths, reverse = reverse)

  def _current_tree(self):
    return self._current_head().tree

  def _current_head(self):
    return self._repo.head.commit

  def __str__(self):
    return "Split(name=%s, remote=%s, paths=%s)" % (self._name, self.remote, self.paths)
