#!/usr/bin/python

from git import Repo
from git.exc import InvalidGitRepositoryError

USAGE = """\
git sap ...
"""

def usage(message):
  print message
  print USAGE
  exit(1)

def open_repo():
  try:
    return Repo()
  except InvalidGitRepositoryError:
    usage("Must be inside a git repository")

repo = open_repo()
print "Using repo at: ", repo.working_tree_dir

tree = repo.branches.master.commit.tree
for entry in tree.traverse():
  print entry.hexsha, entry.type, entry.name, entry.mode, entry.path, entry.abspath

exit(0)
