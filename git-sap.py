#!/usr/bin/python

import git
import gitsap
import optparse
import os

def usage(message, *args):
  print message % args
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

# TODO(jsirois): extract this utility to an appropriate spot
def find(iterable, predicate, default = None):
  for item in iterable:
    if (predicate(item)):
      return item
  if default is None:
    raise KeyError
  return default()

def list(repo, split_config, verbose):
  for split in split_config.splits.values():
    if not verbose:
      print split.name
    else:
      paths = (
        "%s/" % os.path.relpath(os.path.join(repo.working_tree_dir, path)) for path in split.paths
      )
      print "%s\t%s\t%d\n\t%s" % (split.name, split.remote, len(split.paths), "\n\t".join(paths))

def split(repo, split_config, names, verbose):
  for split in (split_config.splits[name] for name in names):
    if (verbose):
      print "Operating on split: %s" % split

    parent = None
    branch_name = 'sapling_split_%s' % split.name
    branch = find(repo.branches,
                  lambda branch: branch.name == branch_name,
                  lambda: repo.create_head(branch_name))

    index = git.IndexFile(repo)
    for subtree in split.subtrees():
      print "Adding subtree %s to index %s" % (subtree, index)
      index.add(subtree)
    synthetic_tree = index.write_tree()

    parent = git.Commit.create_from_tree(repo, synthetic_tree, "git-sap split",
                                         parent_commits = parent, head = True)
    branch.commit = parent
    print "%s\t[%s]" % (parent.hexsha, branch.name)

def main():
  repo = open_repo()
  split_config = open_config(repo)

  usage = """
    %prog (-d) --list
    %prog (-d) --split [splitname...]"""

  parser = optparse.OptionParser(usage = usage, version = "%prog 0.1")
  parser.add_option("-d", "--debug", dest = "debug", action = "store_true", default = False,
                    help = "prints extra debugging information")
  parser.add_option("-v", "--verbose", dest = "verbose", action = "store_true", default = False,
                    help = "prints extra information")
  parser.add_option("--list",
                    dest = "subcommand",
                    default = "list",
                    action = "store_const",
                    const = "list",
                    help = """lists the defined splits""")
  parser.add_option("--split",
                    dest = "subcommand",
                    action = "store_const",
                    const = "split",
                    help =
                    """populates the [splitname] branch with commits intersecting the split""")
  (options, args) = parser.parse_args()

  if options.debug:
    print "repo\t[%s]\t%s" % (repo.active_branch, repo.working_tree_dir)

  if options.subcommand is "list":
    if len(args) != 0:
      parser.error("list takes no arguments")
    list(repo, split_config, options.verbose)

  elif options.subcommand is "split":
    if len(args) == 0:
      parser.error("At least 1 split must be specified")
    try:
      split(repo, split_config, args, options.verbose)
    except KeyError as e:
      parser.error("split not defined: %s" % e)

try:
  main()
  exit(0)
except object as e:
  usage(e)


# TODO(jsirois): kill this cruft
#for name, split in splitConfig.splits.items():
#  print "Found split: %s" % name
#
#  for i, commit in enumerate(split.commits()):
#    fileinfos = map(lambda obj: obj.path,
#                    commit.tree.traverse(predicate = lambda obj, depth: isinstance(obj, git.Blob),
#                                         visit_once = True))
#
#    print "[%d] %s %s %s\n%s\t%s" % (i, commit.hexsha, commit.committed_date, commit.committer,
#                                     commit.message, "\n\t".join(fileinfos))
