== Installation:

Install the python library and git porcelain script you can use easy_install to install from the
PyPI registry: http://pypi.python.org/pypi/sapling
$ sudo easy_install sapling

Or you can get the source distribution and run the following from its root:
$ sudo python setup.py install

Then link the porcelain into git-core
$ sudo sapling.py --install

Get help
$ git sap -h

== Configuration

Sapling (git sap) is configured with a .saplings file at the root of your git repository.  Here's
an example .saplings configuration for a scala project with common component and a hack component
that uses it:

common = {
  # The logical name of the split - listed by git sap.
  'name': 'common',

  # The default remote to associate this split with - currently ignored but required.
  'remote': 'file:/tmp/common.git',

  # The paths that comprise this split.  These paths will form the saplings split from and merged
  # into your repository when using git sap --split and git sap --merge respectively
  'paths': [
    'project',
    'src/main/scala/com/twitter/common',
    'src/main/resources/com/twitter/common',
    'src/test/scala/com/twitter/common',
  ]
}

hack = {
  'name': 'hack',
  'remote': 'file:/tmp/hack.git',
  'paths': [
    'project',
    'src/main/scala/com/twitter/hack',
  ]
}

# This is all git sap looks for - a list of splits named 'splits'.  Each split in the list must be
# a dict with the keys shown/described above.
splits = [
  common,
  hack
]

== Use

To verify your .saplings is correct, you can view the current splits (assuming .saplings above)
with:
$ git sap
common
hack

You could split out the common split to a new repo like so:
$ git sap --split common
$ git push git@github.com:jsirois/common.git sapling_split_common:master

You can merge changes back in from a split branch or repo with:
$ git pull -s recursive -X ours git@github.com:jsirois/common.git master

== Development:

To run all tests, you can use something like:
$ PYTHONPATH=$PYTHONPATH:. py.test test/*.py -v

