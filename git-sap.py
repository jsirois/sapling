#!/usr/bin/python

import git
import gitsap
import os
import stat

USAGE = """git sap ...
"""

def usage(message):
  print message
  print USAGE
  exit(1)

def open_repo():
  try:
    return git.Repo()
  except git.exc.InvalidGitRepositoryError:
    usage("Must be inside a git repository")

def open_config(repo):
  config_path = os.path.join(repo.working_tree_dir, '.saplings')
  if os.path.exists(config_path):
    with open(config_path, 'r') as config:
      try:
        return gitsap.Config(repo, config.read())
      except gitsap.ConfigError as e:
        usage("Problem loading .saplings config: %s" % e)
  else:
    return gitsap.Config(repo)

repo = open_repo()
print "Using repo: %s [%s]" % (repo.working_tree_dir, repo.active_branch)

splitConfig = open_config(repo)
for name, split in splitConfig.splits.items():
  print "Found split: %s" % name
  for subtree in split.subtrees():
    # TODO(jsirois): remove this logging
    print "\tFound subtree at path %s" % subtree.path
    for entry in subtree.traverse():
      print "\t\t", entry.hexsha, entry.type, stat.S_IMODE(entry.mode), entry.path

exit(0)
