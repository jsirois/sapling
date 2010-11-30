import os

def version():
  """Returns the current version of sapling"""

  with open(os.path.join(os.path.dirname(__file__), 'version.txt'), 'r') as version:
    return version.read().strip()
