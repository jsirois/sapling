import git
import gitdb
import lib
import os
import StringIO

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

  def commits(self, branch = None, reverse = True):
    head = self._current_head()
    revspec = head if branch is None else "%s ^%s" % (head.hexsha, self._repo.branch())
    return git.Commit.iter_items(self._repo, head, self.paths, reverse = reverse)

  def apply(self, branch_name, commits = None,
            on_commit = lambda original_commit, new_commit: None):
    """Applies this split over the given commits (or self.commits() if None) to the named branch
and returns the tip commit.  An on_commit callback can be passed to track progress of the split."""

    parent = None
    branch = lib.find(self._repo.branches,
                      lambda branch: branch.name == branch_name,
                      lambda: self._repo.create_head(branch_name))

    for commit in (self.commits() if commits is None else commits):
      index_path = '/tmp/%s.index' % branch_name
      if os.path.exists(index_path):
        os.remove(index_path)

      index = git.IndexFile(self._repo, index_path)
      for item in self._subtrees(commit):
        if item.type is "blob":
          index.add(item,)
        else:
          index.add(item.traverse(lambda item, depth: item.type is "blob"))
      synthetic_tree = index.write_tree()
      parent = git.Commit(self._repo, git.Commit.NULL_BIN_SHA, synthetic_tree, commit.author,
                          commit.authored_date, commit.author_tz_offset, commit.committer,
                          commit.committed_date, commit.committer_tz_offset,
                          "%s\n(sapling split of %s)" % (commit.message, commit.hexsha),
                          [] if parent is None else [ parent ], commit.encoding)

      stream = StringIO.StringIO()
      parent._serialize(stream)
      stream_len = stream.tell()
      stream.seek(0)

      istream = self._repo.odb.store(gitdb.IStream(git.Commit.type, stream_len, stream))
      parent.binsha = istream.binsha

      if (on_commit):
        on_commit(commit, parent)

    branch.commit = parent
    return parent

  def _subtrees(self, commit = None, ignore_not_found = True):
    if commit is None:
      commit = self._current_head()

    for path in self.paths:
      try:
        yield commit.tree / path
      except KeyError as e:
        if not ignore_not_found:
          raise e

  def _current_tree(self):
    return self._current_head().tree

  def _current_head(self):
    return self._repo.head.commit

  def __str__(self):
    return "Split(name=%s, remote=%s, paths=%s)" % (self._name, self.remote, self.paths)
