import os

def find(iterable, predicate, default = None):
  """ Finds and returns the first item in iterable that passes the supplied predicate.  If not item
  matches and a default was not specified then a KeyError is raised; otherwise, the default is
  returned"""

  for item in iterable:
    if (predicate(item)):
      return item

  if default is None:
    raise KeyError

  if callable(default):
    return default()
  else:
    return default

def with_line_numbers(string):
  lines = string.splitlines()
  width = len(str(len(lines)))
  return os.linesep.join([str(i + 1).rjust(width) + ' ' + line for (i, line) in enumerate(lines)])
