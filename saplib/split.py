import git
import gitdb
import lib
import os
import re
import StringIO

class Split(object):
  """Represents a split of a git repository off to a remote repository.  A Split maps one or more
  subtrees of a containing git repository as a logical unit that can be pushed to or pulled from its
  remote."""

  __slots__ = ('_repo', '_name', '_paths', '_excludes')

  def __init__(self, repo, name, patterns):
    """Creates a new Split over the given repo with the specified logical name.  The patterns
    specify paths to include in the split and regular expressions to prune out sub-paths.  Paths to
    include are taken as relative to the root of the repo and can either be directory paths, in
    which case the full directory tree is retained in the split, or an individual file path.
    Excludes are distinguished with a leading ! character with the rest of the pattern forming a
    path regular expression to match files gathered from the path patterns that should be pruned.

    For example, the following patterns would specify a split that grabs a top-level README, and the
    src/ tree except for any OWNERS files contained within:
    [ 'README', 'src', '!.+/OWNERS$"""

    self._repo = repo
    self._name = name

    paths = []
    excludes = set()
    for pattern in patterns:
      if pattern.startswith('!'):
        excludes.add(re.compile(pattern[1:]))
      else:
        paths.append(os.path.normpath(pattern))
    self.paths = paths
    self._excludes = excludes

  @property
  def name(self):
    """The logical name of this Split."""
    return self._name

  @property
  def paths(self):
    "The paths this split is comprised of."
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

  def commits(self, reverse = True):
    """Returns an iterator over the commits in the current head that instersect this split.  By
    default commits are returned oldest first, but this can be overridden by specifying
    'reverse' = False"""

    refspec = self._current_head()
    return git.Commit.iter_items(self._repo, refspec, self.paths, reverse = reverse)

  class ApplyListener(object):
    def on_start(self, commit_count):
      pass
    def on_commit(self, original_commit, new_commit):
      pass
    def on_finish(self):
      pass

  def apply(self, branch_name, apply_listener = ApplyListener()):
    """Applies this split over the commits to the named branch and returns the tip commit. An
    ApplyListener callback can be passed to track progress of the split; otherwise, a no-op
    ApplyListener is used. If there are no (new) commits to split None is returned."""

    commits = list(self.commits())
    if not commits:
      return None

    commit_count = len(commits)

    apply_listener.on_start(commit_count)
    try:
      if not commits:
        return None

      parent = None
      branch = lib.find(self._repo.branches,
                        lambda branch: branch.name == branch_name,
                        lambda: self._repo.create_head(branch_name))

      for commit in commits:
        index_path = '/tmp/%s.index' % branch_name
        if os.path.exists(index_path):
          os.remove(index_path)

        index = git.IndexFile(self._repo, index_path)
        for item in self._subtrees(commit):
          if self._is_included(item):
            index.add([item])
          else:
            index.add(item.traverse(lambda item, depth: self._is_included(item)))
        synthetic_tree = index.write_tree()

        parents = [] if parent is None else [ parent ]
        parent = self._copy_commit(commit, synthetic_tree, parents)
        apply_listener.on_commit(commit, parent)

      branch.commit = parent
      return parent

    finally:
      apply_listener.on_finish()

  def _copy_commit(self, orig_commit, tree, parents):
    new_commit = git.Commit(self._repo, git.Commit.NULL_BIN_SHA, tree, orig_commit.author,
                            orig_commit.authored_date, orig_commit.author_tz_offset,
                            orig_commit.committer, orig_commit.committed_date,
                            orig_commit.committer_tz_offset,
                            "%s\n(sapling split of %s)" % (orig_commit.message, orig_commit.hexsha),
                            parents, orig_commit.encoding)

    return self._write_commit(new_commit)

  def _write_commit(self, commit):
    stream = StringIO.StringIO()
    commit._serialize(stream)

    stream_len = stream.tell()
    stream.seek(0)

    istream = self._repo.odb.store(gitdb.IStream(git.Commit.type, stream_len, stream))
    commit.binsha = istream.binsha
    return commit

  def _subtrees(self, commit = None, ignore_not_found = True):
    if commit is None:
      commit = self._current_head_commit()

    for path in self.paths:
      try:
        yield commit.tree / path
      except KeyError as e:
        if not ignore_not_found:
          raise e

  def _is_included(self, item):
    return item.type is "blob" and not self._is_excluded(item)

  def _is_excluded(self, item):
    for exclude in self._excludes:
      if exclude.match(item.path):
        return True
    return False

  def _current_tree(self):
    return self._current_head_commit().tree

  def _current_head_commit(self):
    return self._current_head().commit

  def _current_head(self):
    return self._repo.head

  def __str__(self):
    return "Split(name=%s, paths=%s, excludes=%s)" % (
      self._name,
      self.paths,
      [ exclude.pattern for exclude in self._excludes ]
    )
