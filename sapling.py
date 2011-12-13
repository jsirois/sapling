#!/usr/bin/env python
from __future__ import print_function
from __builtin__ import list as pylist

from sapversion import version

import git
import optparse
import os
import saplib
import subprocess
import sys

def log(message, *args, **kwargs):
  print(message % args, file = sys.stderr, **kwargs)

def usage(message, *args):
  print(message % args)
  exit(1)

def open_repo(native = True):
  try:
    return git.Repo(odbt = git.db.GitCmdObjectDB if native else git.db.GitDB)
  except git.exc.InvalidGitRepositoryError:
    usage("Must be inside a git repository")

def open_config(repo):
  config_path = os.path.join(repo.working_tree_dir, '.saplings')
  if os.path.exists(config_path):
    with open(config_path, 'r') as config:
      try:
        return saplib.Config(repo, config.read())
      except saplib.ConfigError as e:
        usage("Problem loading .saplings config: %s", e)
  else:
    return saplib.Config(repo)

def install(show = False, force = False):
  git_exec_path = subprocess.Popen(["git", "--exec-path"],
                                   stdout = subprocess.PIPE).communicate()[0].strip()
  installed_link_path = os.path.join(git_exec_path, 'git-sap')

  if show:
    print(os.path.realpath(installed_link_path))
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
      print("symlink %s at: %s" % ("re-installed" if recreate else "installed",
                                   installed_link_path))
    except OSError as e:
      usage("failed to install symlink: %s", e)

  else:
    print("symlink exists: %s" % installed_link_path)

def list(repo, split_config, verbose):
  for split in split_config.splits.values():
    print(split.name)
    if verbose:
      paths = (
        "%s/" % os.path.relpath(os.path.join(repo.working_tree_dir, path)) for path in split.paths
      )
      log("paths (%d):\n\t%s", len(split.paths), "\n\t".join(paths))

def split(splits, verbose, dry_run):
  for split in splits:
    if (verbose):
      log("Operating on split: %s", split)

    # TODO(jsirois): allow customization of branch, consider special names:
    # name1:branch1 name2 ... nameN:branchN
    branch_name = '_sapling_split_%s_' % split.name

    if dry_run:
      commits = pylist(split.commits())
      print("Would split %d new commits to branch: %s" % (len(commits), branch_name))
      print("\n".join(commit.hexsha for commit in commits))
      return

    class ProgressTracker(saplib.Split.ApplyListener):
      def __init__(self):
        self._commit_index = 0
        self._width = 80.0
        self._pct = 0
        self._pct_complete = 0

      def on_start(self, commit_count):
        self._commit_count = commit_count
        message = "[split = %s, branch = %s] Processing %d commits" % (split.name,
                                                                       branch_name,
                                                                       self._commit_count)
        if verbose:
          log(message)
        else:
          self._width = max(len(message) + 2.0, float(self._width))
          self._quantum = self._commit_count / self._width
          log(message + (" " * (int(self._width) - len(message) - 1)) + "|")

      def on_commit(self, original_commit, new_commit):
        self._commit_index += 1

        if verbose:
          log("%s -> %s (%d of %d)", original_commit.hexsha, new_commit.hexsha, self._commit_index,
              self._commit_count)
        else:
          self._pct_complete = int(self._commit_index / self._quantum % self._commit_count)
          if self._pct_complete > self._pct:
            log("." * (self._pct_complete - self._pct), end = "")
            self._pct = self._pct_complete
            sys.__stdout__.flush()

      def on_finish(self):
        if not verbose:
          log("." * (int(self._width) - self._pct_complete))

    tip = split.apply(branch_name, apply_listener = ProgressTracker())

    if (tip):
      print(tip.hexsha)
    else:
      log("No new commits to split.")

def parse_args():
  versionMessage = "%prog {0} (http://pypi.python.org/pypi/sapling/{0})".format(version())

  usage = """
    %prog (-dv --python-git-db) --list
    %prog (-dv --python-git-db) --split [splitname...]"""

  epilog = "Happy splitting!"

  parser = optparse.OptionParser(usage = usage, version = versionMessage, epilog = epilog)

  parser.add_option("-d", "--debug", dest = "debug", action = "store_true", default = False,
                    help = "Prints extra debugging information.")
  parser.add_option("-v", "--verbose", dest = "verbose", action = "store_true", default = False,
                    help = "Prints extra information.")
  parser.add_option("--python-git-db", dest = "native", action = "store_false", default = True,
                    help = "Specifies the python implementation of the git object database should "
                    "be used instead of the native one - can speed operations when repository has "
                    "few large files.")

  # TODO(jsirois): enforce mutual exclusivity of these option groups

  install = optparse.OptionGroup(parser, "Install sap as a git subcommand")
  install.add_option("--install",
                     dest = "subcommand",
                     action = "store_const",
                     const = "install",
                     help = "Installs the git sap command if not installed already.")
  install.add_option("-f", "--force",
                     dest = "force",
                     action = "store_true",
                     default = False,
                     help = "Forces a re-install of the git sap command.")
  install.add_option("-s", "--show",
                     dest = "show",
                     action = "store_true",
                     default = False,
                     help = "Does not perform an install, instead shows the path of the binary "
                     "git sap' calls into.")
  parser.add_option_group(install)

  list = optparse.OptionGroup(parser, "List configured splits for the current git repo")
  list.add_option("--list",
                    dest = "subcommand",
                    default = "list",
                    action = "store_const",
                    const = "list",
                    help = "Lists splits defined in .saplings if any.")
  parser.add_option_group(list)

  split = optparse.OptionGroup(parser, "Split new commits out that affect one or more splits")
  split.add_option("--split",
                    dest = "subcommand",
                    action = "store_const",
                    const = "split",
                    help = "Populates branches with commits intersecting the specified splits. "
                           "If a --branch is not specified, arguments are treated as split names "
                           "definied in the .saplings config.")
  split.add_option("-b", "--branch",
                    dest = "branch",
                    help = "Specifies a branch to split to, arguments are treated as the patterns "
                           "to split.")
  split.add_option("-n", "--dry-run",
                   dest = "dry_run",
                   action = "store_true",
                   default = False,
                   help = "Does not perform a split, instead just lists the commits that would be "
                   "split.")
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

  # Fail fast if we're not in a repo
  repo = open_repo(options.native)

  if options.debug:
    print("repo\t[%s]\t%s" % (repo.active_branch, repo.working_tree_dir))

  if options.subcommand is "list":
    # Fail fast if we don't have an invalid .saplings config
    split_config = open_config(repo)

    if len(args) != 0:
      ferror("list takes no arguments")

    list(repo, split_config, options.verbose)

  elif options.subcommand is "split":
    if options.branch:
      if len(args) == 0:
        ferror("At least 1 split path must be specified")

      try:
        splits = [ saplib.Split(repo, options.branch, args) ]
      except KeyError as e:
        ferror(e)
    else:
      if len(args) == 0:
        ferror("At least 1 split must be specified")

      splits_by_name = open_config(repo).splits
      try:
        splits = [ splits_by_name[name] for name in args ]
      except KeyError as e:
        ferror("Split not defined: %s" % e)

    split(splits, options.verbose, options.dry_run)

try:
  main()
  exit(0)
except object as e:
  usage(e)
