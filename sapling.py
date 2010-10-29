#!/usr/bin/env python

import git
import optparse
import os
import saplib
import subprocess
import sys

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
        return saplib.Config(repo, config.read())
      except saplib.ConfigError as e:
        usage("Problem loading .saplings config: %s" % e)
  else:
    return saplib.Config(repo)

def install(show = False, force = False):
  git_exec_path = subprocess.Popen(["git", "--exec-path"],
                                   stdout = subprocess.PIPE).communicate()[0].strip()
  installed_link_path = os.path.join(git_exec_path, 'git-sap')

  if show:
    print os.path.realpath(installed_link_path)
    return

  recreate = force and os.path.exists(installed_link_path)
  if recreate:
    try:
      os.remove(installed_link_path)
    except OSError as e:
      usage("failed to remove old symlink: %s", e)

  if not os.path.exists(installed_link_path):
    try:
      os.symlink(os.path.abspath(sys.argv[0]), installed_link_path)
      print("symlink %s at: %s" % ("re-installed" if recreate else "installed", installed_link_path))
    except OSError as e:
      usage("failed to install symlink: %s", e)

  else:
    print("symlink exists: %s" % installed_link_path)

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
    branch = saplib.find(repo.branches,
                         lambda branch: branch.name == branch_name,
                         lambda: repo.create_head(branch_name))

    index_path = '/tmp/%s.index' % branch_name
    index = git.IndexFile(repo, index_path)

    try:
      commits = __builtins__.list(split.commits())
      commit_count = len(commits)
      print "Processing %d commits" % commit_count

      for i, commit in enumerate(commits):
        print "[%s] (%d of %d)" % (commit.hexsha, i + 1, commit_count)
        for item in split.subtrees(commit):
          if verbose:
              print "Adding %s %s at path %s" % (item.type, item.hexsha, item.path)
          if item.type is "blob":
            index.add(item,)
          else:
            index.add(item.traverse(lambda item, depth: item.type is "blob"))
        synthetic_tree = index.write_tree()
        parent = git.Commit.create_from_tree(repo,
                                             synthetic_tree,
                                             "sapling split of %s" % commit.hexsha,
                                             parent_commits = [] if parent is None else [ parent ],
                                             head = False)

      branch.commit = parent
      print "%s\t[%s]" % (parent.hexsha, branch.name)
    finally:
      if os.path.exists(index_path):
        os.remove(index_path)

def parse_args():
  usage = """
    %prog (-d) --list
    %prog (-d) --split [splitname...]"""

  epilog = "Happy splitting!"

  parser = optparse.OptionParser(usage = usage, version = "%prog 0.0.1", epilog = epilog)
  parser.add_option("-d", "--debug", dest = "debug", action = "store_true", default = False,
                    help = "prints extra debugging information")
  parser.add_option("-v", "--verbose", dest = "verbose", action = "store_true", default = False,
                    help = "prints extra information")

  # TODO(jsirois): enforce mutual exclusivity of these option groups

  install = optparse.OptionGroup(parser, "Install sap as a git subcommand")
  install.add_option("--install",
                     dest = "subcommand",
                     action = "store_const",
                     const = "install",
                     help = """installs the git sap command if not installed already""")
  install.add_option("-f", "--force",
                     dest = "force",
                     action = "store_true",
                     default = False,
                     help = """forces a re-install of the git sap command""")
  install.add_option("-s", "--show",
                     dest = "show",
                     action = "store_true",
                     default = False,
                     help = "does not perform an install, instead shows the path of the binary "
                     "git sap' calls into")
  parser.add_option_group(install)

  list = optparse.OptionGroup(parser, "List configured splits for the current git repo")
  list.add_option("--list",
                    dest = "subcommand",
                    default = "list",
                    action = "store_const",
                    const = "list",
                    help = """lists the defined splits""")
  parser.add_option_group(list)

  split = optparse.OptionGroup(parser, "Split new commits out that affect one or more splits")
  split.add_option("--split",
                    dest = "subcommand",
                    action = "store_const",
                    const = "split",
                    help =
                    """populates the [splitname] branch with commits intersecting the split""")
  parser.add_option_group(split)

  (options, args) = parser.parse_args()
  return (options, args, parser.error)

def main():
  (options, args, ferror) = parse_args()

  if options.subcommand is "install":
    if len(args) != 0:
      ferror("list takes no arguments")
    install(options.show, options.force)
    return

  # Fail fast if we're either not in a repo or we are but have an invalid .saplings config
  repo = open_repo()
  split_config = open_config(repo)

  if options.debug:
    print "repo\t[%s]\t%s" % (repo.active_branch, repo.working_tree_dir)

  if options.subcommand is "list":
    if len(args) != 0:
      ferror("list takes no arguments")
    list(repo, split_config, options.verbose)

  elif options.subcommand is "split":
    if len(args) == 0:
      ferror("At least 1 split must be specified")
    try:
      split(repo, split_config, args, options.verbose)
    except KeyError as e:
      ferror("split not defined: %s" % e)

try:
  main()
  exit(0)
except object as e:
  usage(e)
